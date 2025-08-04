# File: backend-python/utils/AIAnalysis/modules/building.py

def analyze_building(events):
    """
    Analyze player's building efficiency and patterns.
    """
    building_stats = {
        "structures_built": 0,
        "materials_used": {
            "wood": 0,
            "brick": 0,
            "metal": 0
        },
        "defensive_builds": 0,
        "aggressive_builds": 0,
        "edits_made": 0,
        "build_fights": 0
    }

    for event in events:
        if event["type"] == "build":
            building_stats["structures_built"] += 1
            mat = event.get("material")
            if mat in building_stats["materials_used"]:
                building_stats["materials_used"][mat] += 1
            if event.get("style") == "defensive":
                building_stats["defensive_builds"] += 1
            elif event.get("style") == "aggressive":
                building_stats["aggressive_builds"] += 1
        elif event["type"] == "edit":
            building_stats["edits_made"] += 1
        elif event["type"] == "build_fight":
            building_stats["build_fights"] += 1

    return building_stats
