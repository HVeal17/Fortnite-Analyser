import os
import json
from datetime import datetime
from pathlib import Path

from utils.AIAnalysis.match_analysis import run_match_analysis
from utils.AIAnalysis.feedback.llm_assistant import generate_ai_feedback  # Placeholder for LLM


# Root directory of the entire project
ROOT_DIR = Path(__file__).resolve().parents[2]
TRAINING_DATA_DIR = ROOT_DIR / "training_data"
TRAINING_DATA_DIR.mkdir(exist_ok=True)

# def handle_new_replay(parsed_data: dict, output_dir: str):
#     """
#     Process a parsed replay: run analysis, generate feedback, and save training data.
#     """
#     # 1. Run statistical analysis
#     results = run_match_analysis(parsed_data, output_dir)

#     # 2. Generate feedback (LLM or template)
#     feedback = generate_ai_feedback(results)

#     # 3. Save feedback to feedback.json
#     feedback_path = os.path.join(output_dir, "feedback.json")
#     with open(feedback_path, "w", encoding="utf-8") as f:
#         json.dump(feedback, f, indent=2)
#     print(f"✅ Saved feedback to {feedback_path}")

#     # 4. Save analysis + replay input + feedback for LLM training later
#     log = {
#         "input": {
#             "events": parsed_data.get("events", []),
#             "analysis": results
#         },
#         "output": {
#             "feedback": feedback
#         }
#     }

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     example_path = TRAINING_DATA_DIR / f"match_{timestamp}.json"
#     with open(example_path, "w", encoding="utf-8") as f:
#         json.dump(log, f, indent=2)
#     print(f"📁 Saved LLM training example to: {example_path}")

# --- ADDED FUNCTION ---

def handle_new_replay(parsed_data: dict, output_dir: str):
    """
    Process a parsed replay: run analysis, generate feedback, and save training data.
    """

    # 🔍 Debug: Print parsed data summary
    print("🔎 Parsed replay summary:")
    for key, section in parsed_data.items():
        if isinstance(section, dict):
            print(f"  {key}: {[k for k in section.keys()]}")
        else:
            print(f"  {key}: {type(section)}")

    # 🛑 Sanity check: detect clearly broken data
    if all(
        isinstance(section, dict) and all(v == 0 or v == 0.0 or v == [] or v == {} for v in section.values())
        for section in parsed_data.get("analysis", {}).values()
        if isinstance(section, dict)
    ):
        print("⚠️  Warning: All analysis data is zero or empty. Replay may not have parsed correctly.")
        print("🧪 Skipping analysis and feedback generation.")
        return  # Optional: skip further processing

    # 1. Run statistical analysis
    results = run_match_analysis(parsed_data, output_dir)

    # 2. Generate feedback (LLM or template)
    feedback = generate_ai_feedback(results)


from utils.fortnite_replay_parser import ReplayParser

def parse_and_analyze(replay_path: Path):
    """
    End-to-end parse and analysis for a replay file.
    """
    print(f"📥 Starting parse for: {replay_path.name}")
    
    try:
        replay = ReplayParser(str(replay_path))
        replay.parse()
        parsed_data = replay.to_dict()

        output_dir = Path("database/analysis_results") / replay_path.stem
        output_dir.mkdir(parents=True, exist_ok=True)

        handle_new_replay(parsed_data, str(output_dir))

    except Exception as e:
        print(f"❌ Failed to parse and analyze {replay_path.name}: {e}")

