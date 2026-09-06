"""
Road511 API — reading a whole feature set with cursor pagination
Sign up at https://portal.road511.com for a free API key

Cursor (keyset) pagination is the way to walk a large set. Unlike `offset`, its
cost does not grow with depth and it has no ceiling — which matters because
several single type + jurisdiction sets are larger than the offset cap.

    export ROAD511_API_KEY="YOUR_API_KEY"
    pip install requests
    python python_features_paging.py
"""

import os

import requests

BASE_URL = "https://api.road511.com/api/v1"
API_KEY = os.environ.get("ROAD511_API_KEY")
if not API_KEY:
    raise SystemExit("Set ROAD511_API_KEY environment variable")

HEADERS = {"X-API-Key": API_KEY}


def iter_features(**filters):
    """Yield every feature matching the filters, one page at a time.

    Three rules the API enforces:
      * never send `cursor` and `offset` together — that is a 400;
      * stop when `has_more` is false, where `next_cursor` is absent;
      * treat the cursor as opaque — echo it back, do not parse or build one.
    """
    cursor = None
    while True:
        params = dict(filters)
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(f"{BASE_URL}/features", headers=HEADERS, params=params)
        resp.raise_for_status()
        body = resp.json()

        yield from body["data"]

        if not body["has_more"]:
            return
        cursor = body["next_cursor"]


# --- Example: bridge clearances in Texas ---
# This set is larger than the offset cap, so `offset` cannot reach its end.
print("=== Bridge clearances in TX ===")

count = 0
with_clearance = 0
lowest = None

for feature in iter_features(type="bridge_clearances", jurisdiction="TX", limit=100):
    count += 1

    # Properties are source-specific and sparse: not every bridge publishes a
    # clearance, and numeric-looking values sometimes arrive as strings. Read
    # them defensively rather than assuming a shape.
    raw = (feature.get("properties") or {}).get("clearance_ft")
    try:
        clearance = float(raw)
    except (TypeError, ValueError):
        clearance = None

    if clearance is not None:
        with_clearance += 1
        if lowest is None or clearance < lowest[0]:
            lowest = (clearance, feature.get("name") or feature["id"])

    # Remove this guard to walk the whole set; it keeps the demo short.
    if count >= 500:
        print("  (stopping the demo at 500 — drop the guard to read them all)")
        break

print(f"  Read {count} features, {with_clearance} of them with a published clearance")
if lowest:
    print(f"  Lowest clearance seen: {lowest[0]} ft at {lowest[1]}")

# --- The same walk with offset, for comparison ---
# Correct, but each page costs more than the last, and it stops at the cap.
#
#     offset = 0
#     while True:
#         body = requests.get(
#             f"{BASE_URL}/features", headers=HEADERS,
#             params={"type": "bridge_clearances", "jurisdiction": "TX",
#                     "limit": 100, "offset": offset},
#         ).json()
#         ...
#         if not body["has_more"]:
#             break
#         offset += 100
