"""
Road511 API — the analytics endpoints
Sign up at https://portal.road511.com for a free API key

Every endpoint here needs a Pro+ plan; on lower tiers they answer 403 with an
upgrade hint rather than an error you have to guess at. Together they answer
questions the live feeds cannot: how long incidents take to clear, which
corridors misbehave, whether weather correlates with what you are seeing, and
how a planned end date drifted before the work actually finished.

    export ROAD511_API_KEY="YOUR_API_KEY"
    pip install requests
    python python_analytics.py
"""

import os
from datetime import date, timedelta

import requests

BASE_URL = "https://api.road511.com/api/v1"
API_KEY = os.environ.get("ROAD511_API_KEY")
if not API_KEY:
    raise SystemExit("Set ROAD511_API_KEY environment variable")

HEADERS = {"X-API-Key": API_KEY}

TO = date.today()
FROM = TO - timedelta(days=30)


def get(path, **params):
    """Call an analytics endpoint, naming the plan gate rather than raising on it."""
    resp = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params)
    if resp.status_code == 403:
        print(f"  {path}: needs a Pro+ plan — {resp.json().get('error', '403')}")
        return None
    resp.raise_for_status()
    return resp.json()


def head(rows, n=3):
    """These endpoints return either a bare array or a paged envelope."""
    if rows is None:
        return []
    return (rows["data"] if isinstance(rows, dict) and "data" in rows else rows)[:n]


# --- Where incidents cluster ---
print("=== Hotspots ===")
for row in head(get("/analytics/hotspots", jurisdiction="WA")):
    print(f"  {row}")

# --- How long they take to clear (P50 / P95) ---
print("\n=== Clearance times ===")
for row in head(get("/analytics/clearance", jurisdiction="WA")):
    print(f"  {row}")

# --- Which corridors are worst ---
print("\n=== Corridor reliability ===")
for row in head(get("/analytics/corridors", jurisdiction="WA")):
    print(f"  {row}")

# --- Counts over time ---
print("\n=== Trends ===")
for row in head(get("/analytics/trends", jurisdiction="WA")):
    print(f"  {row}")

# --- Jurisdictions ranked against each other ---
print("\n=== Scorecard ===")
for row in head(get("/analytics/scorecard", country="US", **{"from": FROM.isoformat()},
                    to=TO.isoformat(), rank_by="events", order="desc", limit=5)):
    print(f"  {row}")

# --- Probability of an incident in a given hour ---
print("\n=== Forecast: I-5 in WA, Friday 17:00 ===")
forecast = get("/analytics/forecast", jurisdiction="WA", road="I-5", dow=5, hour=17)
if forecast:
    print(f"  computed_at={forecast.get('computed_at')} bucket={forecast.get('bucket')}")

# --- Event lifecycle: the changes feed, and one event's timeline ---
print("\n=== Recent lifecycle changes ===")
changes = get("/analytics/changes", limit=5)
for row in head(changes, 5):
    print(f"  {row}")

if changes and changes.get("data"):
    event_id = changes["data"][0].get("event_id") or changes["data"][0].get("id")
    if event_id:
        print(f"\n=== Timeline for event {event_id} ===")
        for row in head(get(f"/analytics/history/{event_id}"), 5):
            print(f"  {row}")

        # Conditions at the nearest weather station when the event was created.
        print(f"\n=== Weather snapshot for event {event_id} ===")
        snap = get(f"/analytics/event-weather/{event_id}")
        if snap:
            print(f"  {snap.get('distance_km')} km away: {snap.get('temperature')}, "
                  f"surface {snap.get('road_surface')}, {snap.get('precipitation')}")

# --- Feature lifecycle: created / deactivated / schedule drift ---
print("\n=== Feature history (schedule drift) ===")
for row in head(get("/analytics/feature-history", change_type="end_time_change", limit=5), 5):
    print(f"  {row}")

# --- Weather readings, and whether they correlate with incidents ---
print("\n=== Weather readings ===")
for row in head(get("/analytics/weather", jurisdiction="WA", limit=3)):
    print(f"  {row}")

print("\n=== Weather / incident correlation ===")
for row in head(get("/analytics/weather-correlation", jurisdiction="WA",
                    **{"from": FROM.isoformat()}, to=TO.isoformat(), max_dist_km=25, limit=5)):
    print(f"  {row}")
