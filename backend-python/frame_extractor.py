import cv2
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import av


def extract_frames_optimized(video_path, output_dir, max_workers=4, use_ffmpeg=False):
    os.makedirs(output_dir, exist_ok=True)

    if use_ffmpeg:
        for hwaccel in ["d3d11va", "dxva2", "auto"]:
            try:
                print(f"⚡ Trying FFmpeg with hwaccel: {hwaccel}...")
                cmd = [
                    "ffmpeg",
                    "-hwaccel", hwaccel,
                    "-i", video_path,
                    "-q:v", "1",
                    os.path.join(output_dir, "frame_%05d.jpg")
                ]
                subprocess.run(cmd, check=True)
                print(f"✅ FFmpeg completed with '{hwaccel}'. Frames saved in '{output_dir}'")
                return
            except subprocess.CalledProcessError as e:
                print(f"❌ FFmpeg failed with hwaccel '{hwaccel}': {str(e)}")
        print("❌ All FFmpeg hwaccel attempts failed.")
        return

    try:
        container = av.open(video_path)
        stream = container.streams.video[0]
        stream.thread_type = "AUTO"
        total_frames = stream.frames
        fps = stream.average_rate

        print(f"🎥 FPS: {fps}")
        print(f"🎞️ Total Frames in video: {total_frames}")
        print(f"📸 Target: Extracting {total_frames} frames (every frame)...")

        saved_count = 0

        def save_frame(image, count):
            filename = f"frame_{count:05d}.jpg"
            path = os.path.join(output_dir, filename)
            success = cv2.imwrite(path, image)
            if not success:
                print(f"❌ Failed to save frame at count: {count}")
            elif count % 10000 == 0:
                print(f"✅ {count} frames saved so far...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for frame in container.decode(stream):
                img = frame.to_ndarray(format="bgr24")
                futures.append(executor.submit(save_frame, img, saved_count))
                saved_count += 1

                if len(futures) >= max_workers * 4:
                    for future in as_completed(futures[:max_workers]):
                        future.result()
                    futures = futures[max_workers:]

            for future in as_completed(futures):
                future.result()

        print(f"✅ Done: {saved_count} frames scheduled for saving in '{output_dir}'")

    except Exception as e:
        print(f"❌ Exception during extraction: {str(e)}")


# AUTOMATION ENTRY POINT
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    video_dir = os.path.join(base_dir, "..", "Videos")
    frames_dir = os.path.join(base_dir, "..", "ExtractedFrames")

    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(frames_dir, exist_ok=True)

    video_files = [f for f in os.listdir(video_dir) if f.lower().endswith((".mp4", ".mov", ".mkv"))]
    if not video_files:
        print(f"⚠️ No video file found in '{video_dir}'")
    else:
        video_file = os.path.join(video_dir, video_files[0])
        print(f"🎯 Found video: {video_file}")
        output_folder = os.path.join(frames_dir, os.path.splitext(video_files[0])[0])

        # 🔀 Change to True to use FFmpeg + GPU decode
        extract_frames_optimized(video_file, output_folder, use_ffmpeg=True)
