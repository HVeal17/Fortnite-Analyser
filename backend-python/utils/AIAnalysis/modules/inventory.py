# File: backend-python/utils/AIAnalysis/modules/inventory.py

def analyze_inventory(events):
    """
    Analyze inventory usage over the match.
    """
    inventory_stats = {
        "items_collected": {},
        "items_dropped": {},
        "healing_items_used": 0,
        "utility_items_used": 0,
    }

    healing_items = {"medkit", "bandage", "slurp_juice", "shield_potion", "mini_shield"}
    utility_items = {"shockwave_grenade", "impulse_grenade", "port-a-fort", "launch_pad"}

    for event in events:
        item = event.get("item")
        if not item:
            continue

        if event["type"] == "item_collected":
            inventory_stats["items_collected"][item] = (
                inventory_stats["items_collected"].get(item, 0) + 1
            )
        elif event["type"] == "item_dropped":
            inventory_stats["items_dropped"][item] = (
                inventory_stats["items_dropped"].get(item, 0) + 1
            )
        elif event["type"] == "item_used":
            if item in healing_items:
                inventory_stats["healing_items_used"] += 1
            elif item in utility_items:
                inventory_stats["utility_items_used"] += 1

    return inventory_stats
