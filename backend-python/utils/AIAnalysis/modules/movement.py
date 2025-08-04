# File: backend-python/utils/AIAnalysis/modules/movement.py

def analyze_movement(events):
    """
    Analyze player movement during the match.
    """
    movement_stats = {
        "distance_traveled": 0.0,
        "sprint_time": 0.0,
        "walk_time": 0.0,
        "jump_count": 0,
        "zipline_used": 0,
    }

    for event in events:
        if event["type"] == "movement":
            movement_stats["distance_traveled"] += event.get("distance", 0.0)
            if event.get("mode") == "sprint":
                movement_stats["sprint_time"] += event.get("duration", 0.0)
            elif event.get("mode") == "walk":
                movement_stats["walk_time"] += event.get("duration", 0.0)
        elif event["type"] == "jump":
            movement_stats["jump_count"] += 1
        elif event["type"] == "zipline_used":
            movement_stats["zipline_used"] += 1

    movement_stats["distance_traveled"] = round(movement_stats["distance_traveled"], 2)
    movement_stats["sprint_time"] = round(movement_stats["sprint_time"], 2)
    movement_stats["walk_time"] = round(movement_stats["walk_time"], 2)

    return movement_stats
