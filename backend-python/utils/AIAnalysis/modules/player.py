# File: backend-python/utils/AIAnalysis/modules/player.py

def analyze_player(events):
    """
    Analyze player-level performance such as survival, health status, and placement.
    """
    player_stats = {
        "time_alive": 0,
        "placement": None,
        "health_remaining": 0,
        "shield_remaining": 0,
        "revives": 0,
        "reboots": 0
    }

    for event in events:
        if event["type"] == "match_end":
            player_stats["placement"] = event.get("placement")
        elif event["type"] == "time_alive":
            player_stats["time_alive"] = event.get("duration", 0)
        elif event["type"] == "health_update":
            player_stats["health_remaining"] = event.get("health", 0)
            player_stats["shield_remaining"] = event.get("shield", 0)
        elif event["type"] == "revive":
            player_stats["revives"] += 1
        elif event["type"] == "reboot":
            player_stats["reboots"] += 1

    return player_stats
