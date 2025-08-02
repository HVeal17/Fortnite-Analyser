import os
import uuid
import yt_dlp

def download_video(link: str, output_dir: str) -> str:
    
    os.makedirs(output_dir, exist_ok=True)

    # Final file path (fixed .mp4 name)
    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(output_dir, filename)

    # yt-dlp options — simple and proven
    ydl_opts = {
        # Best separate video+audio; fallback to progressive best
        "format": "bestvideo+bestaudio/best",
        # Write directly to the final path (mp4)
        "outtmpl": output_path,
        # Ensure merged file is MP4
        "merge_output_format": "mp4",
        # Keep it simple; let yt-dlp log normally
        "quiet": False,
    }

    # If ffmpeg isn't on PATH, you can hardcode its location here:
    # ydl_opts["ffmpeg_location"] = r"C:\ffmpeg\bin"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    return output_path
