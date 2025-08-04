# File: backend-python/utils/AIAnalysis/modules/summary.py

def generate_match_summary(analysis_results):
    """
    Summarize analysis across all modules.
    """
    summary = {
        "kills": analysis_results.get("combat", {}).get("eliminations", 0),
        "accuracy": analysis_results.get("combat", {}).get("accuracy", 0.0),
        "rotation_score": analysis_results.get("rotation", {}).get("score", 0),
        "positioning_score": analysis_results.get("positioning", {}).get("score", 0),
        "zone_safety": analysis_results.get("zone", {}).get("time_in_zone", 0),
    }
    return summary