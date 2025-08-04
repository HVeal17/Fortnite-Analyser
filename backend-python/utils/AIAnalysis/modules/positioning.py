# File: backend-python/utils/AIAnalysis/modules/positioning.py

def analyze_positioning(events):
    """
    Analyze player positioning quality based on elevation, cover, and exposure.
    """
    pos_stats = {
        "time_in_cover": 0,
        "time_in_open": 0,
        "time_on_high_ground": 0,
        "exposed_time": 0,
        "score": 0
    }

    for event in events:
        if event["type"] == "position":
            pos_stats["time_in_cover"] += event.get("in_cover", 0)
            pos_stats["time_in_open"] += event.get("in_open", 0)
            pos_stats["time_on_high_ground"] += event.get("high_ground", 0)
            pos_stats["exposed_time"] += event.get("exposed", 0)

    # Compute a basic positioning score
    safe_time = pos_stats["time_in_cover"] + pos_stats["time_on_high_ground"]
    total_time = safe_time + pos_stats["time_in_open"] + pos_stats["exposed_time"]
    if total_time > 0:
        pos_stats["score"] = round((safe_time / total_time) * 100, 2)

    return pos_stats
