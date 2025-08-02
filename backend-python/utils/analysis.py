import os
import json
import time
import math
from typing import List, Tuple, Optional, Dict

import cv2
import numpy as np

# --- Utility helpers ---------------------------------------------------------

def _sorted_frame_paths(frames_dir: str) -> List[str]:
    files = [f for f in os.listdir(frames_dir) if f.lower().endswith(".jpg")]
    files.sort()  # frame_00000.jpg, frame_00001.jpg, ...
    return [os.path.join(frames_dir, f) for f in files]

def _load_gray(path: str) -> Optional[np.ndarray]:
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return img

def _estimate_fps_from_video(video_path: str) -> Optional[float]:
    if not os.path.exists(video_path):
        return None
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    if fps and fps > 0:
        return float(fps)
    return None

# --- Motion-based action segmentation ---------------------------------------

def find_action_segments(
    frames_dir: str,
    fps: float,
    diff_threshold: float = 12.0,     # tune: higher = fewer segments
    min_duration_s: float = 2.0,      # merge short bursts
    sample_every: int = 1             # 1 = every frame; 2 = every other frame
) -> List[Tuple[int, int, float]]:
    """
    Returns a list of (start_idx, end_idx, score) where each is an "action" window.
    Uses mean absolute difference between consecutive grayscale frames as motion proxy.
    """
    paths = _sorted_frame_paths(frames_dir)
    if len(paths) < 2:
        return []

    # Read first frame
    prev = _load_gray(paths[0])
    if prev is None:
        return []

    diffs = []
    # Compute motion signal
    for i in range(sample_every, len(paths), sample_every):
        cur = _load_gray(paths[i])
        if cur is None or cur.shape != prev.shape:
            prev = cur
            diffs.append(0.0)
            continue
        diff = cv2.absdiff(cur, prev)
        score = float(diff.mean())
        diffs.append(score)
        prev = cur

    # Smooth the signal a bit (moving average)
    window = max(3, int(round(0.25 * (fps / sample_every))))  # ~0.25s window
    kernel = np.ones(window, dtype=np.float32) / window
    smooth = np.convolve(np.array(diffs, dtype=np.float32), kernel, mode="same")

    # Threshold into segments
    above = smooth > diff_threshold
    segments = []
    start = None
    for idx, is_on in enumerate(above):
        if is_on and start is None:
            start = idx
        elif not is_on and start is not None:
            end = idx
            segments.append((start, end))
            start = None
    if start is not None:
        segments.append((start, len(above)))

    # Merge tiny segments and compute scores
    min_len = int(min_duration_s * (fps / sample_every))
    merged: List[Tuple[int, int, float]] = []
    for (s, e) in segments:
        if e - s < min_len:
            continue
        seg_scores = smooth[s:e]
        merged.append((s, e, float(seg_scores.mean())))

    # Convert indices from sampled timeline back to full-frame indices
    full_segments = []
    for (s, e, sc) in merged:
        full_segments.append((s * sample_every, e * sample_every, sc))
    return full_segments

# --- Optional: Kill feed OCR -------------------------------------------------

def _try_import_easyocr():
    try:
        import easyocr  # type: ignore
        return easyocr
    except Exception:
        return None

def ocr_kill_feed(
    frames_dir: str,
    roi: Optional[Tuple[int, int, int, int]] = None,
    sample_every_frames: int = 5,
    keywords: Tuple[str, ...] = ("eliminated", "elim", "knocked")
) -> List[Dict]:
    """
    Naive OCR over a region-of-interest where kill feed usually appears.
    roi = (x, y, w, h) in pixels relative to frame size. If None, uses top-left heuristic.
    Returns list of dicts: {frame_idx, text}
    """
    reader_mod = _try_import_easyocr()
    if reader_mod is None:
        return []

    paths = _sorted_frame_paths(frames_dir)
    if not paths:
        return []

    # Determine default ROI from first frame if not provided
    first = cv2.imread(paths[0], cv2.IMREAD_COLOR)
    if first is None:
        return []
    H, W = first.shape[:2]
    if roi is None:
        # Heuristic: top-left 35% width x 25% height
        roi = (0, 0, int(W * 0.35), int(H * 0.25))

    x, y, w, h = roi
    reader = reader_mod.Reader(["en"], gpu=False)

    events = []
    for i in range(0, len(paths), sample_every_frames):
        img = cv2.imread(paths[i], cv2.IMREAD_COLOR)
        if img is None:
            continue
        crop = img[y : y + h, x : x + w]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        # Slight blur to reduce noise for OCR
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        result = reader.readtext(gray, detail=0)
        if not result:
            continue

        text = " ".join(result).lower()
        if any(k in text for k in keywords):
            events.append({"frame_idx": i, "text": text})

    return events

# --- Orchestrator ------------------------------------------------------------

def run_analysis(
    video_path: str,
    frames_dir: str,
    output_dir: str,
    fps_hint: Optional[float] = None,
    run_ocr: bool = False,
    roi: Optional[Tuple[int, int, int, int]] = None,
) -> Dict:
    """
    End-to-end analysis using saved frames.
    Produces report.json and (optionally) segments.csv.
    """
    os.makedirs(output_dir, exist_ok=True)

    # FPS – prefer real video FPS if available
    fps = fps_hint or _estimate_fps_from_video(video_path) or 30.0

    # 1) Motion-based action windows
    segments = find_action_segments(
        frames_dir=frames_dir,
        fps=fps,
        diff_threshold=12.0,
        min_duration_s=2.0,
        sample_every=1,
    )

    # 2) Optional OCR of kill feed
    kill_events = ocr_kill_feed(frames_dir, roi=roi, sample_every_frames=5) if run_ocr else []

    # Build summary
    total_frames = len(_sorted_frame_paths(frames_dir))
    duration_s = total_frames / fps if fps > 0 else 0.0

    # Derive fight/rotation metrics
    action_time_s = sum((e - s) / fps for (s, e, _) in segments)
    action_pct = (action_time_s / duration_s * 100) if duration_s > 0 else 0.0
    avg_action_len = np.mean([(e - s) / fps for (s, e, _) in segments]) if segments else 0.0

    report = {
        "video_path": video_path,
        "frames_dir": frames_dir,
        "fps": fps,
        "total_frames": total_frames,
        "duration_sec": duration_s,
        "action_segments": [
            {"start_frame": s, "end_frame": e, "score": sc, "start_sec": s / fps, "end_sec": e / fps}
            for (s, e, sc) in segments
        ],
        "action_summary": {
            "num_segments": len(segments),
            "total_action_time_sec": action_time_s,
            "action_percent": action_pct,
            "avg_action_segment_sec": float(avg_action_len),
        },
        "kill_events": kill_events,
    }

    # Save report.json
    with open(os.path.join(output_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Also write simple CSV of segments
    try:
        csv_path = os.path.join(output_dir, "segments.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write("start_frame,end_frame,score,start_sec,end_sec\n")
            for (s, e, sc) in segments:
                f.write(f"{s},{e},{sc:.3f},{s / fps:.3f},{e / fps:.3f}\n")
    except Exception:
        pass

    return report
