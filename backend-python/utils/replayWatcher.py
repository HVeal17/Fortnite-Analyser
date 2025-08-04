# File: backend-python/utils/ReplayWatcher.py

import os
import time
import json
from pathlib import Path
from utils.ReplayGetter import parse_and_analyze

REPLAY_FOLDER = Path(os.path.expandvars(r"%localappdata%\FortniteGame\Saved\Demos"))
PROCESSED_LOG = Path("database/processed_replays.json")
POLL_INTERVAL = 30  # seconds

# Load or initialize processed replays list
if PROCESSED_LOG.exists():
    with open(PROCESSED_LOG, "r") as f:
        processed = set(json.load(f).get("processed", []))
else:
    processed = set()

def start_replay_watcher():
    print(f"👀 Watching for new replays in: {REPLAY_FOLDER}")
    print(f"✅ {len(processed)} replay(s) already processed.")

    try:
        while True:
            for replay_path in REPLAY_FOLDER.glob("*.replay"):
                if replay_path.name in processed:
                    continue

                try:
                    print(f"🆕 New replay found: {replay_path.name}")
                    parse_and_analyze(replay_path)
                    processed.add(replay_path.name)
                    with open(PROCESSED_LOG, "w") as f:
                        json.dump({"processed": list(processed)}, f)
                except Exception as e:
                    print(f"❌ Error parsing {replay_path.name}: {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("👋 Stopping Replay Watcher.")

# Standalone execution
if __name__ == "__main__":
    start_replay_watcher()
