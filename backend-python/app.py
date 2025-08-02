from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import threading
import subprocess
import shutil
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed

# If your downloader is in utils/downloader.py
from utils.downloader import download_video

app = Flask(__name__)
CORS(app)

# ---- Canonical absolute paths (avoid 'videos' vs 'Videos' mismatch) ----
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
VIDEO_DIR = os.path.join(PROJECT_ROOT, "Videos")
FRAMES_ROOT = os.path.join(PROJECT_ROOT, "ExtractedFrames")
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(FRAMES_ROOT, exist_ok=True)


def log_line(log_fp, msg: str):
    print(msg, flush=True)
    try:
        log_fp.write(msg + "\n")
        log_fp.flush()
    except Exception:
        pass


def extract_frames_optimized(video_path: str, output_dir: str, max_workers: int = 4):
    """
    CPU-only, safe extractor with bounded memory usage.
    Writes progress to console and to output_dir/extract.log.
    Falls back to ffmpeg CLI (CPU-only) if OpenCV cannot open the video.
    """
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "extract.log")
    with open(log_path, "a", buffering=1, encoding="utf-8") as log_fp:
        log_line(log_fp, f"🟣 Starting extraction for: {video_path}")
        log_line(log_fp, f"📂 Output dir: {output_dir}")

        # Quick sanity check
        if not os.path.exists(video_path):
            log_line(log_fp, f"❌ Video does not exist: {video_path}")
            return
        if os.path.getsize(video_path) == 0:
            log_line(log_fp, f"❌ Video file is empty (0 bytes): {video_path}")
            return

        # --- Try OpenCV path first ---
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            log_line(log_fp, "⚠️ OpenCV could not open the video. Trying ffmpeg fallback...")
            return ffmpeg_fallback(video_path, output_dir, log_fp)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        log_line(log_fp, f"🎞️ Total frames reported: {total_frames} | 🎥 FPS: {fps:.2f}")

        saved_count = 0
        futures = []

        def save_frame(path, frame, index):
            success = cv2.imwrite(path, frame)
            if not success:
                log_line(log_fp, f"❌ Failed to save frame at index {index}")
            elif index % 10000 == 0 and index != 0:
                log_line(log_fp, f"✅ {index} frames saved so far...")

        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_path = os.path.join(output_dir, f"frame_{saved_count:05d}.jpg")
                    futures.append(executor.submit(save_frame, frame_path, frame, saved_count))
                    saved_count += 1

                    # Bound the queue to keep RAM usage under control
                    if len(futures) >= max_workers * 4:
                        for fut in as_completed(futures[:max_workers]):
                            fut.result()
                        futures = futures[max_workers:]

                # Final flush
                for fut in as_completed(futures):
                    fut.result()

            log_line(log_fp, f"✅ Done: {saved_count} frames saved in '{output_dir}'")
        except Exception as e:
            log_line(log_fp, f"❌ Exception during OpenCV extraction: {e}")
            # Try ffmpeg fallback if anything blows up mid-way
            ffmpeg_fallback(video_path, output_dir, log_fp)
        finally:
            cap.release()


def ffmpeg_fallback(video_path: str, output_dir: str, log_fp):
    """
    CPU-only ffmpeg frame extraction. Requires ffmpeg in PATH or provide full path.
    """
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        log_line(log_fp, "❌ ffmpeg not found on PATH. Skipping ffmpeg fallback.")
        return

    cmd = [
        ffmpeg_path,
        "-hide_banner", "-loglevel", "error", "-nostdin",
        "-i", video_path,
        "-vsync", "0",           # do not drop/duplicate
        "-q:v", "2",             # lower is better quality; raise to 3-5 to speed up / reduce IO
        os.path.join(output_dir, "frame_%05d.jpg"),
    ]
    log_line(log_fp, f"🛠 Running ffmpeg fallback: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        log_line(log_fp, f"✅ ffmpeg completed. Frames saved in '{output_dir}'")
    except subprocess.CalledProcessError as e:
        log_line(log_fp, f"❌ ffmpeg failed: {e}")


def start_extraction_background(video_path: str, frames_dir: str):
    """
    Launch extraction on a daemon thread so Flask can return immediately.
    """
    os.makedirs(frames_dir, exist_ok=True)
    t = threading.Thread(
        target=extract_frames_optimized,
        args=(video_path, frames_dir),
        kwargs={"max_workers": 4},
        daemon=True,
    )
    t.start()


@app.route("/upload", methods=["POST"])
def upload():
    print("✅ /upload endpoint called", flush=True)

    try:
        link = request.form.get("link")
        file = request.files.get("video")
        saved_path = None

        print(f"🔗 Link received: {link}", flush=True)
        print(f"📁 File received: {file.filename if file else 'None'}", flush=True)

        # Download or save upload
        if link:
            saved_path = download_video(link, VIDEO_DIR)
            print(f"📥 Video downloaded to: {saved_path}", flush=True)
        elif file:
            filename = file.filename
            # If empty/odd name, assign a UUID
            if not filename or filename.strip() == "":
                import uuid
                filename = f"{uuid.uuid4()}.mp4"
            saved_path = os.path.join(VIDEO_DIR, filename)
            file.save(saved_path)
            print(f"📤 Video uploaded and saved to: {saved_path}", flush=True)
        else:
            return jsonify({"error": "No file or link provided"}), 400

        # Sanity check before extraction
        if not os.path.exists(saved_path):
            return jsonify({"error": f"Saved file not found: {saved_path}"}), 500
        if os.path.getsize(saved_path) == 0:
            return jsonify({"error": f"Saved file is empty: {saved_path}"}), 500

        # Derive output frames folder and kick off extraction in background
        video_name = os.path.splitext(os.path.basename(saved_path))[0]
        frames_output_dir = os.path.join(FRAMES_ROOT, video_name)
        print(f"🛠 Frame extraction triggered → {frames_output_dir}", flush=True)
        start_extraction_background(saved_path, frames_output_dir)

        return jsonify({
            "message": "Video uploaded. Frame extraction started.",
            "videoPath": saved_path,
            "framesDir": frames_output_dir
        })

    except Exception as e:
        print("❌ Error in upload():", str(e), flush=True)
        return jsonify({"error": str(e)}), 500
    
def coach_from_stats(summary: dict) -> list[str]:
    msgs = []
    if summary["elims"] >= 8:
        msgs.append("You had a solid 8+ eliminations—strong offensive pressure.")
    if summary["accuracy_pct"] < 22:
        msgs.append("Accuracy is under 22%. Focus on crosshair placement and micro-adjust flicks.")
    if summary["avg_edit_ms"] > 180:
        msgs.append("Edit confirms are slow; drill single-tile edits to under 150ms.")
    if summary["action_pct"] < 25:
        msgs.append("Low action %. Consider faster rotations and third-partying fights.")
    return msgs

if __name__ == "__main__":
    # Run from backend-python directory so relative paths are stable
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"VIDEO_DIR: {VIDEO_DIR}")
    print(f"FRAMES_ROOT: {FRAMES_ROOT}")
    app.run(port=5000, debug=True, use_reloader=False)
