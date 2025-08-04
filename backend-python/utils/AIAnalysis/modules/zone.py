# File: backend-python/utils/AIAnalysis/modules/zone.py

def analyze_zone_safety(events):
    """
    Analyze player zone behavior including storm time and safe zone entries.
    """
    zone_stats = {
        "time_in_zone": 0,
        "time_in_storm": 0,
        "zone_entries": 0,
        "storm_damage_taken": 0,
    }

    for event in events:
        if event["type"] == "zone_enter":
            zone_stats["zone_entries"] += 1
            zone_stats["time_in_zone"] += event.get("duration", 0)
        elif event["type"] == "storm":
            zone_stats["time_in_storm"] += event.get("duration", 0)
            zone_stats["storm_damage_taken"] += event.get("damage", 0)

    zone_stats["storm_exposure_ratio"] = round(
        zone_stats["time_in_storm"] / (zone_stats["time_in_zone"] + zone_stats["time_in_storm"] + 1e-6), 2
    )

    return zone_stats
