# File: backend-python/utils/AIAnalysis/utils.py

import math
from typing import Tuple, Dict, List

def calculate_distance_2d(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance in 2D (x, y) space."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def calculate_distance_3d(pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
    """Calculate Euclidean distance in 3D (x, y, z) space."""
    return math.sqrt(
        (pos1[0] - pos2[0])**2 +
        (pos1[1] - pos2[1])**2 +
        (pos1[2] - pos2[2])**2
    )

def is_in_zone(player_pos: Tuple[float, float], zone_center: Tuple[float, float], zone_radius: float) -> bool:
    """Check if player is within the safe zone."""
    return calculate_distance_2d(player_pos, zone_center) <= zone_radius

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a number between min and max values."""
    return max(min_val, min(value, max_val))

def extract_player_positions(events: List[Dict]) -> List[Tuple[float, float]]:
    """
    Extract player positions from replay event data.
    Logs skipped events without valid position data.
    """
    positions = []
    for event in events:
        if event.get("type") != "player_movement":
            print(f"ℹ️ Skipped non-movement event type: {event.get('type')}")
            continue

        loc = event.get("location")
        if loc and isinstance(loc, dict):
            x = loc.get("x")
            y = loc.get("y")
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                positions.append((x, y))
            else:
                print(f"⚠️ Skipped invalid coordinates in event: {event}")
        else:
            print(f"⚠️ Skipped event with no location: {event}")
    return positions

from pathlib import Path

def ensure_project_dirs():
    base_dirs = ["database", "training_data"]
    for d in base_dirs:
        Path(d).mkdir(exist_ok=True)
