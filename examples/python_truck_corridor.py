"""
Road511 API — Truck corridor query example
Find bridge clearances, weight restrictions, and truck restrictions along a route.

Sign up at https://portal.road511.com for a free API key (Pro plan required for truck data)

Usage:
    export ROAD511_API_KEY="sk_live_..."
    pip install requests
    python python_truck_corridor.py
"""

import os
import requests

BASE_URL = "https://api.road511.com/api/v1"
API_KEY = os.environ.get("ROAD511_API_KEY")
if not API_KEY:
    raise SystemExit("Set ROAD511_API_KEY environment variable")

headers = {"X-API-Key": API_KEY}


def truck_corridor(**params):
    """Query truck restrictions along a corridor."""
    resp = requests.get(f"{BASE_URL}/truck/corridor", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


# --- Example: I-80 corridor from NYC to Chicago ---
print("=== Truck restrictions: I-80 NYC → Chicago ===")
print("  (bridges, weight limits, truck restrictions within 5km of route)\n")

data = truck_corridor(
    road="I-80",
    from_lat=40.71,   # New York City
    from_lng=-74.01,
    to_lat=41.88,     # Chicago
    to_lng=-87.63,
    buffer_km=5,
    limit=100,
)

# Group results by type
by_type = {}
for item in data.get("data", []):
    t = item["feature_type"]
    by_type.setdefault(t, []).append(item)

for feature_type, items in sorted(by_type.items()):
    print(f"--- {feature_type} ({len(items)} found) ---")
    for item in items[:5]:  # Show first 5 per type
        props = item.get("properties", {})
        name = item.get("name", "Unknown")

        if feature_type == "bridges":
            clearance = props.get("min_clearance_m", "?")
            weight = props.get("weight_limit_tons", "?")
            print(f"  {name}: clearance={clearance}m, weight={weight}t")

        elif feature_type == "weight_restrictions":
            limit_val = props.get("weight_limit_tons", "?")
            print(f"  {name}: limit={limit_val}t")

        elif feature_type == "truck_routes":
            route_type = props.get("route_type", "?")
            print(f"  {name}: {route_type}")

        else:
            print(f"  {name}")

    if len(items) > 5:
        print(f"  ... and {len(items) - 5} more")
    print()

print(f"Total restrictions in corridor: {data.get('total', len(data.get('data', [])))}")
