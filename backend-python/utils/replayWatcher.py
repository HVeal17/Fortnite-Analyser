import os, time, threading, requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Fortnite Replay folder (Windows)
REPLAY_DIR = os.path.expanduser(r"~\AppData\Local\FortniteGame\Saved\Demos")
API_URL = "http://localhost:5219/replay/analyze"  # C# backend endpoint

class ReplayHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        if not event.src_path.lower().endswith(".replay"): return
        threading.Thread(target=process_replay, args=(event.src_path,), daemon=True).start()

def process_replay(path):
    # Wait until file is fully written (growing stops)
    last_size = -1
    while True:
        try:
            size = os.path.getsize(path)
            if size == last_size:
                break
            last_size = size
            time.sleep(1.0)
        except FileNotFoundError:
            return  # removed
    print(f"🟣 New replay detected: {path}")
    try:
        with open(path, "rb") as f:
            r = requests.post(API_URL, files={"replay": (os.path.basename(path), f)})
        print(f"✅ Replay analyzed: {r.status_code}")
        if r.ok:
            print(r.json())  # or write to disk / forward to UI
        else:
            print("❌ Analyzer error:", r.text)
    except Exception as e:
        print("❌ Failed to submit replay:", e)

def start_watching():
    os.makedirs(REPLAY_DIR, exist_ok=True)
    print("👀 Watching:", REPLAY_DIR)
    obs = Observer()
    handler = ReplayHandler()
    obs.schedule(handler, REPLAY_DIR, recursive=False)
    obs.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == "__main__":
    start_watching()
