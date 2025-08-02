import cv2
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

def extract_frames_optimized(video_path, output_dir, max_workers=4, use_ffmpeg=False):
    """
    Extract every frame from a video.
    - CPU-only (no GPU).
    - If use_ffmpeg=True, uses ffmpeg CLI without any hwaccel flags.
    - Otherwise uses OpenCV with a bounded thread pool to limit RAM.
    """
    os.makedirs(output_dir, exist_ok=True)

    if use_ffmpeg:
        print("⚙️ Using FFmpeg (CPU-only)...")
        cmd = [
            "ffmpeg",
            "-hide_banner", "-loglevel", "error", "-nostdin",
            "-i", video_path,
            "-vsync", "0",       # no dup/drop
            "-q:v", "2",         # 1=best, 31=worst; raise to 3–5 to reduce disk I/O
            os.path.join(output_dir, "frame_%05d.jpg"),
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ FFmpeg completed. Frames saved in '{output_dir}'")
        except subprocess.CalledProcessError as e:
            print("❌ FFmpeg failed:", e)
        return

    # --- OpenCV CPU path ---
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open video: {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"🎞️ Total Frames in video: {total_frames}")
    print(f"📸 Extracting every frame using {max_workers} threads")

    saved_count = 0
    futures = []

    def save_frame(p, f, c):
        success = cv2.imwrite(p, f)
        if not success:
            print(f"❌ Failed to save frame at count: {c}")
        elif c % 10000 == 0 and c != 0:
            print(f"✅ {c} frames saved so far...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            path = os.path.join(output_dir, f"frame_{saved_count:05d}.jpg")
            futures.append(executor.submit(save_frame, path, frame, saved_count))
            saved_count += 1

            # Bound the queue to limit RAM (adjust multiplier if needed)
            if len(futures) >= max_workers * 4:
                for fut in as_completed(futures[:max_workers]):
                    fut.result()
                futures = futures[max_workers:]

        # Final flush
        for fut in as_completed(futures):
            fut.result()

    cap.release()
    print(f"✅ Done: {saved_count} frames saved in '{output_dir}'")
