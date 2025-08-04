# File: backend-python/utils/AIAnalysis/feedback/llm_assistant.py

from openai import OpenAI
import json
from pathlib import Path
from datetime import datetime

# Correct relative path
api_key_path = "H:\\git\\Fortnite-Analyser\\backend-python\\utils\\AIAnalysis\\feedback\\.config.json"

with open(api_key_path, "r") as f:
    api_key = json.load(f).get("api_key")

client = OpenAI(api_key=api_key)


# Create training output dir
TRAINING_DATA_DIR = Path("training_data")
TRAINING_DATA_DIR.mkdir(exist_ok=True)


def generate_ai_feedback(match_report: dict) -> str:
    """
    Send structured match data to GPT and receive high-level coaching feedback.
    """
    prompt = build_prompt_from_match(match_report)

    try:
        print("🧠 Sending data to LLM for feedback...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Fortnite coach providing tactical gameplay feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )
        feedback = response.choices[0].message.content.strip()
        print("✅ Feedback received.")

        save_for_training(prompt, feedback)
        return feedback

    except Exception as e:
        print(f"❌ LLM feedback error: {e}")
        return "Unable to generate feedback at this time."


def build_prompt_from_match(report: dict) -> str:
    """
    Turn structured JSON match data into a coaching-friendly prompt.
    """
    summary = report.get("summary", {})
    combat = report.get("combat", {})
    rotation = report.get("rotation", {})
    loadout = report.get("loadout_efficiency", {})
    position = report.get("positioning", {})
    proximity = report.get("enemy_proximity", {})

    prompt = f"""Here's a summary of a player's Fortnite match. Please provide personalized tactical feedback, including positioning, combat decisions, loadout usage, and rotation quality.

MATCH SUMMARY:
- Kills: {summary.get('kills', 0)}
- Accuracy: {summary.get('accuracy', 0.0)}%
- Positioning Score: {summary.get('positioning_score', 0)}
- Rotation Score: {summary.get('rotation_score', 0)}
- Zone Safety Time: {summary.get('zone_safety', 0)} seconds
- Average Enemy Distance: {proximity.get('avg_distance', 0.0)} meters
- Weapons Used: {', '.join(loadout.keys()) if loadout else 'N/A'}

COMBAT:
{json.dumps(combat, indent=2)}

ROTATION:
{json.dumps(rotation, indent=2)}

POSITIONING:
{json.dumps(position, indent=2)}

LOADOUT EFFICIENCY:
{json.dumps(loadout, indent=2)}

ENEMY PROXIMITY:
{json.dumps(proximity, indent=2)}

Please keep your feedback concise but informative.
"""
    return prompt


def save_for_training(prompt: str, response: str):
    """
    Save the input/output for training a custom model later.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file = TRAINING_DATA_DIR / f"sample_{timestamp}.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump({"prompt": prompt, "response": response}, f, indent=2)
