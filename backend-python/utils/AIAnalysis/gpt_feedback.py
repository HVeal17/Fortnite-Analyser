# File: backend-python/utils/AIAnalysis/gpt_feedback.py

import os
import json
import openai

# Load your OpenAI API key from environment or config
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt_for_feedback(analysis_summary: dict) -> str:
    """
    Send analysis summary to GPT-4-turbo and receive feedback in natural language.
    """
    prompt = (
        "You are a professional Fortnite coach. Based on this player's performance summary, "
        "give detailed, personalized feedback and advice for improvement. Structure your response into the following categories:\n"
        "Combat, Rotation, Positioning, Zone Awareness, Loadout Usage, Movement, Building.\n"
        "Be clear and encouraging, and explain what the player did well and what they can improve.\n\n"
        f"Match Summary:\n{json.dumps(analysis_summary, indent=2)}\n"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error communicating with OpenAI: {e}"


# Example use:
if __name__ == "__main__":
    from modules.summary import generate_match_summary
    from match_analysis import run_full_analysis  # You must ensure this is implemented correctly

    summary = generate_match_summary(run_full_analysis("sample_data.json"))
    feedback = ask_gpt_for_feedback(summary)
    print("\n📋 AI Feedback:\n")
    print(feedback)
