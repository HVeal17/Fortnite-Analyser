# File: backend-python/utils/AIAnalysis/modules/loadout_efficiency.py

def analyze_loadout_efficiency(events):
    """
    Evaluate the usage and impact of each item used.
    """
    weapon_stats = {}

    for event in events:
        if event["type"] == "item_used":
            item = event.get("item")
            if item not in weapon_stats:
                weapon_stats[item] = {"uses": 0, "damage": 0}
            weapon_stats[item]["uses"] += 1
        elif event["type"] == "damage" and event.get("source") in weapon_stats:
            weapon_stats[event["source"]]["damage"] += event.get("amount", 0)

    return weapon_stats