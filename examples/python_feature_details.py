"""
Road511 API — feature detail, single and batched
Sign up at https://portal.road511.com for a free API key

List rows are deliberately lean. Where a source publishes more than the list
carries — a camera's stream URL, a rest area's amenities — the row says so with
`has_details: true`, and the detail endpoints fetch it on demand.

    export ROAD511_API_KEY="YOUR_API_KEY"
    pip install requests
    python python_feature_details.py
"""

import os

import requests

BASE_URL = "https://api.road511.com/api/v1"
API_KEY = os.environ.get("ROAD511_API_KEY")
if not API_KEY:
    raise SystemExit("Set ROAD511_API_KEY environment variable")

HEADERS = {"X-API-Key": API_KEY}

# --- Step 1: a list call, to find rows that carry extra detail ---
print("=== Cameras in Ontario ===")
listing = requests.get(
    f"{BASE_URL}/features",
    headers=HEADERS,
    params={"type": "cameras", "jurisdiction": "ON", "limit": 10},
)
listing.raise_for_status()
rows = listing.json()["data"]

detailed = [r for r in rows if r.get("has_details")]
print(f"  {len(rows)} rows, {len(detailed)} of them advertise extra detail")

if not detailed:
    raise SystemExit("  No row carried has_details — try another type or jurisdiction")

# --- Step 2: one feature, in full ---
first = detailed[0]
print(f"\n=== Detail for {first['id']} ===")
resp = requests.get(f"{BASE_URL}/features/{first['id']}/details", headers=HEADERS)
resp.raise_for_status()
detail = resp.json()

# `cache` says where the answer came from. Worth reading rather than ignoring:
#   hit / miss    - served from cache, or fetched upstream just now
#   poll          - this source is enriched during polling, no on-demand fetch
#   none          - no detail loader exists for this source and type
#   retired       - the source stopped listing this id; you get the last known
#                   properties and no upstream call is made
#   error         - the upstream fetch was attempted and failed
#   error-cached  - a recent failure is being replayed; retrying will not help
print(f"  cache={detail['cache']} detail_available={detail['detail_available']}")

props = (detail.get("data") or {}).get("properties") or {}
for key in ("url", "video_url"):
    if props.get(key):
        print(f"  {key}: {props[key]}")
for view in props.get("views") or []:
    print(f"  view {view.get('name')}: {view.get('url')}")

# --- Step 3: many features in one round trip ---
# Prefer this over a loop of single calls: per-id caching is identical, so a
# batch that overlaps an earlier one costs nothing for the overlap. Bounded by
# your plan's max_batch_size and by a system ceiling of 500 ids per request.
print("\n=== Batched detail ===")
ids = [r["id"] for r in detailed[:5]] + ["definitely-not-a-real-id"]
batch = requests.post(
    f"{BASE_URL}/features/details/batch",
    headers=HEADERS,
    json={"ids": ids},
)
batch.raise_for_status()
results = batch.json()

print(f"  asked for {len(ids)}, got {results['count']} results")
for item in results["data"]:
    if item.get("not_found"):
        print(f"  {item['id']}: not found")
        continue
    # A failed id does not fail the batch: it comes back with cache=error and an
    # error string of its own. cache=skipped means the request ran out of time
    # budget before reaching it — that one is worth retrying in a smaller batch.
    if item.get("error"):
        print(f"  {item['id']}: {item['cache']} — {item['error']}")
        continue
    name = (item.get("data") or {}).get("name") or "(unnamed)"
    print(f"  {item['id']}: {item['cache']} — {name}")
