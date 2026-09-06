"""
Road511 API — Python events example
Sign up at https://portal.road511.com for a free API key

Usage:
    export ROAD511_API_KEY="YOUR_API_KEY"
    pip install requests
    python python_events.py
"""

import os
from urllib.parse import quote

import requests

BASE_URL = "https://api.road511.com/api/v1"
API_KEY = os.environ.get("ROAD511_API_KEY")
if not API_KEY:
    raise SystemExit("Set ROAD511_API_KEY environment variable")

headers = {"X-API-Key": API_KEY}


def get_events(**params):
    """Fetch traffic events with optional filters."""
    resp = requests.get(f"{BASE_URL}/events", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


# --- Example 1: Active incidents in Washington state ---
print("=== Active incidents in WA ===")
data = get_events(jurisdiction="WA", type="incident", limit=5)
print(f"Total matching: {data['total']}")
for event in data["data"]:
    roads = ", ".join(event.get("affected_roads") or []) or "—"
    print(f"  [{event['severity']}] {roads}: {event['title']}")

# --- Example 2: Radius search near a location ---
print("\n=== Events within 30km of Portland, OR ===")
data = get_events(lat=45.52, lng=-122.68, radius_km=30, limit=5)
for event in data["data"]:
    print(f"  [{event['type']}] {event['title']}")

# --- Example 3: Construction on a specific road ---
print("\n=== Construction on I-5 ===")
data = get_events(road="I-5", type="construction", limit=5)
for event in data["data"]:
    jur = event["jurisdiction"]
    roads = ", ".join(event.get("affected_roads") or []) or "—"
    print(f"  [{jur}] {roads}: {event['title']}")

# --- Example 4: Paginate through all major events ---
print("\n=== All major events (paginated) ===")
offset = 0
total_fetched = 0
while True:
    data = get_events(severity="major", limit=50, offset=offset)
    events = data["data"]
    if not events:
        break
    total_fetched += len(events)
    offset += len(events)
    # Stop after 150 for demo purposes
    if total_fetched >= 150:
        break

print(f"  Fetched {total_fetched} of {data['total']} major events")

# --- Example 5: Single event by ID ---
if data["data"]:
    event_id = data["data"][0]["id"]
    print(f"\n=== Event detail: {event_id} ===")
    # Percent-encode the id: 116,883 event ids (5.2%) contain characters that are
    # not path-safe, including slashes — e.g. "511SF-511.org/1060526".
    resp = requests.get(f"{BASE_URL}/events/{quote(event_id, safe='')}", headers=headers)
    resp.raise_for_status()
    event = resp.json()
    print(f"  Type: {event['type']}")
    print(f"  Severity: {event['severity']}")
    roads = ", ".join(event.get("affected_roads") or []) or "—"
    print(f"  Roads: {roads}")
    print(f"  Description: {event.get('description', 'N/A')[:120]}")
