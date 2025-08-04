from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from pathlib import Path
import threading

from utils.ReplayGetter import parse_and_analyze
from utils.ReplayWatcher import start_replay_watcher
from utils.AIAnalysis.match_analysis import run_match_analysis
from utils.AIAnalysis.feedback.llm_assistant import generate_ai_feedback
from utils.AIAnalysis.utils import ensure_project_dirs

app = Flask(__name__)
CORS(app)

ensure_project_dirs()

REPLAY_UPLOAD_DIR = os.path.expandvars(r"%localappdata%\FortniteGame\Saved\Demos")

@app.route("/upload", methods=["POST"])
def upload_replay():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    replay_file = request.files["file"]
    save_path = os.path.join(REPLAY_UPLOAD_DIR, replay_file.filename)
    replay_file.save(save_path)

    try:
        print("📦 Parsing new replay...")
        parsed_matches = parse_and_analyze()

        if not parsed_matches:
            return jsonify({"error": "No new matches parsed."}), 500

        latest_report = parsed_matches[-1]
        print("📊 Running match analysis...")
        analysis = run_match_analysis(latest_report)

        # print("🧠 Generating LLM feedback...")
        # feedback = generate_ai_feedback(analysis)

        # return jsonify({
        #     "feedback": feedback,
        #     "summary": analysis.get("summary", {})
        # })

    except Exception as e:
        print(f"❌ Upload processing failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # 👀 Start replay watcher in the background
    watcher_thread = threading.Thread(target=start_replay_watcher, daemon=True)
    watcher_thread.start()

    print("🚀 Starting Flask server...")
    app.run(port=5000)
