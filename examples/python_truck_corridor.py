"""
Road511 API — Truck corridor query example
Find bridge clearances, weight restrictions, and truck restrictions along a route.

Sign up at https://portal.road511.com for a free API key (Pro plan required for truck data)

Usage:
    export ROAD511_API_KEY="YOUR_API_KEY"
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

def first_of(props, *keys):
    """Return the first key that is actually present and non-empty.

    Verified against production: `clearance_ft` appears on ~92k rows,
    `weight_limit_t` on ~10k, `nn_designation` on ~455k truck_routes. An earlier
    version of this file read `max_weight_tonnes` and `route_type`, which do not
    exist on these types — so it printed "?" for every row.
    """
    for k in keys:
        v = props.get(k)
        if v not in (None, "", []):
            return v
    return None


for feature_type, items in sorted(by_type.items()):
    print(f"--- {feature_type} ({len(items)} found) ---")
    for item in items[:5]:  # Show first 5 per type
        props = item.get("properties", {})
        name = item.get("name", "Unknown")

        # Properties are source-specific: the same fact arrives under different
        # keys depending on which agency published it, and often not at all.
        # Read the alternatives in order rather than assuming one name.
        if feature_type in ("bridge_clearances", "bridges"):
            clearance = first_of(props, "clearance_ft", "vertical_clearance_ft")
            if clearance is not None:
                print(f"  {name}: clearance={clearance} ft")
            else:
                print(f"  {name}: no clearance published")

        elif feature_type == "weight_restrictions":
            limit_val = first_of(props, "weight_limit_t", "weight_limit_tons")
            if limit_val is not None:
                print(f"  {name}: limit={limit_val} t ({props.get('restriction_type', 'restriction')})")
            else:
                print(f"  {name}: {props.get('restriction_type', 'restricted')}, no numeric limit published")

        elif feature_type == "truck_routes":
            designation = first_of(props, "nn_designation", "fgts_class", "functional_class")
            print(f"  {name}: {designation if designation is not None else 'no designation published'}")

        else:
            print(f"  {name}")

    if len(items) > 5:
        print(f"  ... and {len(items) - 5} more")
    print()

print(f"Total restrictions in corridor: {data.get('total', len(data.get('data', [])))}")
