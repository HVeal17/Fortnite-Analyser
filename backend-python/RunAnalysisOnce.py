# save as a small test script, e.g. backend-python/run_analysis_once.py
import os
from utils.analysis import run_analysis

BASE = os.path.abspath(os.path.dirname(__file__))
video = os.path.join(BASE, "Videos", "370d4b3a-093b-42b4-81db-339942e258d2.mp4")
frames = os.path.join(BASE, "ExtractedFrames", "370d4b3a-093b-42b4-81db-339942e258d2")
outdir = os.path.join(BASE, "Analysis", "370d4b3a-093b-42b4-81db-339942e258d2")
os.makedirs(outdir, exist_ok=True)

report = run_analysis(video, frames, outdir, run_ocr=True)  # set False to skip OCR
print("Analysis saved to:", outdir)
