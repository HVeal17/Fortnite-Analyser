from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import uuid
from utils.downloader import download_video
import requests

app = Flask(__name__)
CORS(app)

VIDEO_DIR = "../videos"
EXTRACT_SCRIPT = "frame_extractor.py"  # Path to your script
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    print("✅ /upload endpoint called")

    try:
        link = request.form.get("link")
        file = request.files.get("video")
        saved_path = None

        print(f"🔗 Link received: {link}")
        print(f"📁 File received: {file.filename if file else 'None'}")

        # Handle video link or file upload
        if link:
            saved_path = download_video(link, VIDEO_DIR)
            print(f"📥 Video downloaded to: {saved_path}")
        elif file:
            filename = f"{uuid.uuid4()}.mp4"
            saved_path = os.path.join(VIDEO_DIR, filename)
            file.save(saved_path)
            print(f"📤 Video uploaded and saved to: {saved_path}")
        else:
            return jsonify({"error": "No file or link provided"}), 400

        # ▶️ Automatically run the extract_frames.py script on the new video
        extract_command = [
            "python3", EXTRACT_SCRIPT, saved_path  # Assumes script accepts video path as argument
        ]
        subprocess.Popen(extract_command)
        print("🛠 Frame extraction triggered.")

        # You can still call your C# API or return a response now
        return jsonify({"message": "Upload complete, frame extraction started."})

    except Exception as e:
        print("❌ Error in upload():", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)
