from math import dist

def analyze_rotation(events):
    """
    Analyze how the player rotates between safe zones.
    Measures average distance moved, timing of rotations, and zone transition efficiency.
    """
    zone_entries = []
    movement_during_zone = []
    previous_zone_center = None
    last_zone_time = None

    for event in events:
        if event["type"] == "new_zone":
            zone_center = event.get("center")
            zone_time = event.get("time")

            if previous_zone_center and zone_center:
                zone_distance = dist(previous_zone_center, zone_center)
                zone_entries.append({
                    "from": previous_zone_center,
                    "to": zone_center,
                    "distance": zone_distance,
                    "start_time": last_zone_time,
                    "end_time": zone_time,
                    "time_between": zone_time - last_zone_time if last_zone_time else 0,
                })

            previous_zone_center = zone_center
            last_zone_time = zone_time

        elif event["type"] == "movement":
            movement_during_zone.append(event)

    # Evaluate metrics
    avg_rotation_distance = 0.0
    if zone_entries:
        avg_rotation_distance = round(
            sum(z["distance"] for z in zone_entries) / len(zone_entries), 2
        )

    avg_rotation_speed = 0.0
    if movement_during_zone:
        total_distance = 0
        last_pos = None
        for move in movement_during_zone:
            pos = move.get("position")
            if last_pos and pos:
                total_distance += dist(last_pos, pos)
            last_pos = pos
        avg_rotation_speed = round(total_distance / len(movement_during_zone), 2)

    # Simple scoring logic (for early model training and UI)
    score = 100
    if avg_rotation_distance > 100:
        score -= 15
    if avg_rotation_speed < 5:
        score -= 10

    return {
        "rotations": zone_entries,
        "avg_rotation_distance": avg_rotation_distance,
        "avg_rotation_speed": avg_rotation_speed,
        "score": max(score, 0),
    }
