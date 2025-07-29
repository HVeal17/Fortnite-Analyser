from yt_dlp import YoutubeDL
import uuid
import os

def download_video(link, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    unique_id = str(uuid.uuid4())
    filename = os.path.join(output_dir, f"{unique_id}.%(ext)s")

    ydl_opts = {
        'outtmpl': filename,
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'retries': 10,
        'fragment_retries': 10,
        'concurrent_fragment_downloads': 15,
        'throttled_rate': None,  # Remove throttling if detected
        'http_chunk_size': 10485760,  # 10 MB chunks
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        },
        'no_warnings': True,
        'quiet': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    final_path = filename.replace("%(ext)s", "mp4")
    return final_path
