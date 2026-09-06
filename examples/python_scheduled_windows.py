"""
Road511 API — scheduled-window filters on time-bounded features
Sign up at https://portal.road511.com for a free API key

Some feature types are not "here now" facts but planned work with dates:
future_construction, alerts, special_events, truck_restrictions and similar.
For those, four filters select by schedule rather than by what is live:

    starts_after / starts_before   on the projected start
    ends_after   / ends_before     on the projected end

They match the planned times where the source publishes them and fall back to
actual times otherwise. Features carrying no dates at all are excluded from
window queries entirely — that is the point of the filter, not a bug.

    export ROAD511_API_KEY="YOUR_API_KEY"
    pip install requests
    python python_scheduled_windows.py
"""

import os
from datetime import date, timedelta

import requests

BASE_URL = "https://api.road511.com/api/v1"
API_KEY = os.environ.get("ROAD511_API_KEY")
if not API_KEY:
    raise SystemExit("Set ROAD511_API_KEY environment variable")

HEADERS = {"X-API-Key": API_KEY}


def features(**params):
    resp = requests.get(f"{BASE_URL}/features", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()


def show(body, limit=5):
    for row in body["data"][:limit]:
        window = f"{row.get('start_time') or '?'} .. {row.get('end_time') or 'open-ended'}"
        print(f"  [{row['jurisdiction']}] {row.get('name') or row['id']}")
        print(f"      {window}")
    print(f"  ({body['total']} matching)")


today = date.today()
month_out = today + timedelta(days=30)

# --- Everything overlapping a period ---
# Bound both ends to select work that is active at some point in the window:
# it starts before the window closes AND ends after the window opens.
print(f"=== Construction active at some point between {today} and {month_out} ===")
show(features(
    type="future_construction",
    starts_before=month_out.isoformat(),
    ends_after=today.isoformat(),
    limit=5,
))

# --- Work that has not begun yet ---
print("\n=== Construction starting in the next 30 days ===")
show(features(
    type="future_construction",
    starts_after=today.isoformat(),
    starts_before=month_out.isoformat(),
    limit=5,
))

# --- Open-ended work ---
# A feature with a known start and no end matches ends_after but never
# ends_before. Asking for both is how you separate the two populations.
#
# future_construction is used here rather than truck_restrictions on purpose:
# see the sparsity note at the end of this file.
print("\n=== Construction with no published end date ===")
open_ended = features(type="future_construction", ends_after=today.isoformat(), limit=100)
no_end = [r for r in open_ended["data"] if not r.get("end_time")]
print(f"  {len(no_end)} of {len(open_ended['data'])} returned rows are open-ended")
for row in no_end[:5]:
    print(f"  [{row['jurisdiction']}] {row.get('name') or row['id']}")

# --- Dates accept a plain day as well as RFC3339 ---
print("\n=== Special events ending before the end of next month ===")
show(features(
    type="special_events",
    ends_before=(today + timedelta(days=60)).isoformat(),
    limit=5,
))

# --- A word on how sparse these dates are ---
#
# Sources publish schedules unevenly, and a window filter can only match rows
# that carry dates at all. Measured on production, active rows:
#
#     future_construction     1,218 active     515 with a start   109 with an end
#     special_events             99 active      18 with a start    18 with an end
#     truck_restrictions  1,474,364 active     521 with a start    11 with an end
#
# So a window query over truck_restrictions returns a few hundred rows out of a
# million and a half — not because the filter is broken, but because almost no
# source publishes a schedule for a standing restriction. Use windows to find
# planned work; use a plain type query when you want the whole population.
