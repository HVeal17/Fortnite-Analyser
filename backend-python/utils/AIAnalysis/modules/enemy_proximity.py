# File: backend-python/utils/AIAnalysis/modules/enemy_proximity.py

def analyze_enemy_proximity(events):
    """
    Analyze how often and how close enemies were during the match.
    """
    proximity_stats = {
        "encounters": 0,
        "avg_distance": 0.0,
        "close_encounters": 0,
    }
    total_distance = 0

    for event in events:
        if event["type"] == "enemy_spotted":
            distance = event.get("distance", 0)
            total_distance += distance
            proximity_stats["encounters"] += 1
            if distance < 15:
                proximity_stats["close_encounters"] += 1

    if proximity_stats["encounters"]:
        proximity_stats["avg_distance"] = round(
            total_distance / proximity_stats["encounters"], 2
        )

    return proximity_stats
