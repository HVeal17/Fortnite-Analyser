# File: backend-python/utils/AIAnalysis/modules/combat.py

def analyze_combat(events):
    """
    Analyze combat-related events such as eliminations, hits, damage taken/given.
    """
    combat_stats = {
        "eliminations": 0,
        "damage_given": 0,
        "damage_taken": 0,
        "headshots": 0,
        "accuracy": 0.0,
    }
    shots_fired = 0
    shots_hit = 0

    for event in events:
        if event["type"] == "elimination":
            combat_stats["eliminations"] += 1
        elif event["type"] == "damage":
            if event.get("target") == "enemy":
                combat_stats["damage_given"] += event.get("amount", 0)
                shots_hit += 1
            elif event.get("target") == "self":
                combat_stats["damage_taken"] += event.get("amount", 0)
        elif event["type"] == "shot_fired":
            shots_fired += 1
        elif event["type"] == "headshot":
            combat_stats["headshots"] += 1

    if shots_fired:
        combat_stats["accuracy"] = round((shots_hit / shots_fired) * 100, 2)

    return combat_stats