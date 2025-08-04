import os
import json

from utils.AIAnalysis.modules.combat import analyze_combat
from utils.AIAnalysis.modules.movement import analyze_movement
from utils.AIAnalysis.modules.positioning import analyze_positioning
from utils.AIAnalysis.modules.rotation import analyze_rotation
from utils.AIAnalysis.modules.zone import analyze_zone_safety
from utils.AIAnalysis.modules.loadout_efficiency import analyze_loadout_efficiency
from utils.AIAnalysis.modules.enemy_proximity import analyze_enemy_proximity
from utils.AIAnalysis.modules.building import analyze_building
from utils.AIAnalysis.modules.summary import generate_match_summary

from utils.AIAnalysis.feedback.llm_assistant import generate_ai_feedback


def run_match_analysis(parsed_replay: dict, output_dir: str) -> dict:
    """
    Orchestrate full analysis from parsed replay.
    Saves analysis report and AI feedback in output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    events = parsed_replay.get("events", [])
    metadata = parsed_replay.get("metadata", {})

    # Run analysis modules
    combat = analyze_combat(events)
    movement = analyze_movement(events)
    positioning = analyze_positioning(events)
    rotation = analyze_rotation(events)
    zone = analyze_zone_safety(events)
    loadout = analyze_loadout_efficiency(events)
    proximity = analyze_enemy_proximity(events)
    building = analyze_building(events)

    # Summary
    summary = generate_match_summary({
        "combat": combat,
        "movement": movement,
        "positioning": positioning,
        "rotation": rotation,
        "zone": zone,
        "loadout": loadout,
        "enemy_proximity": proximity,
        "building": building,
    })

    # Compile full report
    full_report = {
        "metadata": metadata,
        "analysis": {
            "combat": combat,
            "movement": movement,
            "positioning": positioning,
            "rotation": rotation,
            "zone": zone,
            "loadout": loadout,
            "enemy_proximity": proximity,
            "building": building,
            "summary": summary,
        }
    }

    # Generate AI feedback
    feedback = generate_ai_feedback(full_report)
    full_report["ai_feedback"] = feedback

    # Save outputs
    with open(os.path.join(output_dir, "analysis_full.json"), "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    with open(os.path.join(output_dir, "feedback.txt"), "w", encoding="utf-8") as f:
        f.write(feedback)

    return full_report
