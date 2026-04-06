"""
Road511 API — Python events example
Sign up at https://portal.road511.com for a free API key

Usage:
    export ROAD511_API_KEY="sk_live_..."
    pip install requests
    python python_events.py
"""

import os
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
    print(f"  [{event['severity']}] {event['road_name']}: {event['title']}")

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
    print(f"  [{jur}] {event['road_name']}: {event['title']}")

# --- Example 4: Paginate through all major events ---
print("\n=== All major/critical events (paginated) ===")
offset = 0
total_fetched = 0
while True:
    data = get_events(severity="major,critical", limit=50, offset=offset)
    events = data["data"]
    if not events:
        break
    total_fetched += len(events)
    offset += len(events)
    # Stop after 150 for demo purposes
    if total_fetched >= 150:
        break

print(f"  Fetched {total_fetched} of {data['total']} major/critical events")

# --- Example 5: Single event by ID ---
if data["data"]:
    event_id = data["data"][0]["id"]
    print(f"\n=== Event detail: {event_id} ===")
    resp = requests.get(f"{BASE_URL}/events/{event_id}", headers=headers)
    resp.raise_for_status()
    event = resp.json()
    print(f"  Type: {event['type']}")
    print(f"  Severity: {event['severity']}")
    print(f"  Road: {event['road_name']}")
    print(f"  Description: {event.get('description', 'N/A')[:120]}")
