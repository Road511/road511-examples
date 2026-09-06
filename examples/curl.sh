#!/usr/bin/env bash
# Road511 API — curl examples
# Sign up at https://portal.road511.com for a free API key
#
# Usage: export ROAD511_API_KEY="YOUR_API_KEY" && bash curl.sh

set -euo pipefail

BASE="https://api.road511.com/api/v1"
KEY="${ROAD511_API_KEY:?Set ROAD511_API_KEY environment variable}"
AUTH=(-H "X-API-Key: $KEY")

echo "=== Active events in California ==="
curl -s "${AUTH[@]}" "$BASE/events?jurisdiction=CA&limit=3" | python3 -m json.tool

echo ""
echo "=== Events near Seattle (50km radius) ==="
curl -s "${AUTH[@]}" "$BASE/events?lat=47.6&lng=-122.3&radius_km=50&limit=3" | python3 -m json.tool

echo ""
echo "=== Major incidents on I-95 ==="
curl -s "${AUTH[@]}" "$BASE/events?road=I-95&severity=major&limit=3" | python3 -m json.tool

echo ""
echo "=== Traffic cameras in Colorado (near Denver) ==="
curl -s "${AUTH[@]}" "$BASE/features?type=cameras&jurisdiction=CO&lat=39.7&lng=-104.9&radius_km=50&limit=3" | python3 -m json.tool

echo ""
echo "=== DMS signs in Texas ==="
curl -s "${AUTH[@]}" "$BASE/features?type=signs&jurisdiction=TX&limit=3" | python3 -m json.tool

echo ""
echo "=== Bridge clearances near Chicago ==="
curl -s "${AUTH[@]}" "$BASE/features?type=bridge_clearances&lat=41.88&lng=-87.63&radius_km=30&limit=3" | python3 -m json.tool

echo ""
echo "=== Weight restrictions in Pennsylvania ==="
curl -s "${AUTH[@]}" "$BASE/features?type=weight_restrictions&jurisdiction=PA&limit=3" | python3 -m json.tool

echo ""
echo "=== EV charging stations in Ontario ==="
curl -s "${AUTH[@]}" "$BASE/features?type=ev_charging&jurisdiction=ON&limit=3" | python3 -m json.tool

echo ""
echo "=== Truck corridor: I-90 Chicago to Cleveland ==="
curl -s "${AUTH[@]}" "$BASE/truck/corridor?road=I-90&from_lat=41.88&from_lng=-87.63&to_lat=41.50&to_lng=-81.69&buffer_km=5&limit=5" | python3 -m json.tool

echo ""
echo "=== Events as GeoJSON (Starter+ plan) ==="
curl -s "${AUTH[@]}" "$BASE/events/geojson?jurisdiction=WA&limit=3" | python3 -m json.tool

echo ""
echo "=== All jurisdictions ==="
curl -s "${AUTH[@]}" "$BASE/jurisdictions" | python3 -m json.tool

echo ""
echo "=== Quick stats ==="
curl -s "${AUTH[@]}" "$BASE/stats" | python3 -m json.tool

echo ""
echo "=== Coverage: is it worth asking, before a query comes back empty ==="
# An empty /features or /events result has always meant one of two opposite
# things — we never carried that data, or we carry it and there is nothing
# right now. This endpoint separates them.
curl -s "${AUTH[@]}" "$BASE/coverage?jurisdiction=ON" | python3 -m json.tool

echo ""
echo "=== Data sources: licensing and attribution catalogue ==="
# Who each feed comes from and what you may do with it. Read this before
# redistributing anything.
curl -s "${AUTH[@]}" "$BASE/data-sources" | python3 -m json.tool | head -40

echo ""
echo "=== Fuel prices: latest per jurisdiction ==="
curl -s "${AUTH[@]}" "$BASE/fuel-prices?country=US&fuel_type=diesel&latest=true&limit=5" | python3 -m json.tool

echo ""
echo "=== Fuel prices: a historical series ==="
curl -s "${AUTH[@]}" "$BASE/fuel-prices?jurisdiction=CA&fuel_type=diesel&from=2026-01-01&limit=5" | python3 -m json.tool

echo ""
echo "=== Subscription plans (public — no key needed) ==="
curl -s "$BASE/plans" | python3 -m json.tool | head -30

echo ""
echo "=== Service status (public — no key needed) ==="
# Per-jurisdiction health, open circuits and 7-day uptime.
curl -s "$BASE/status" | python3 -m json.tool | head -30

echo ""
echo "=== Health check (public) ==="
curl -s "$BASE/health" | python3 -m json.tool

echo ""
echo "=== Feature and jurisdiction taxonomies ==="
curl -s "${AUTH[@]}" "$BASE/features/groups" | python3 -m json.tool | head -20
curl -s "${AUTH[@]}" "$BASE/jurisdictions/groups" | python3 -m json.tool | head -20

echo ""
echo "=== Batched feature detail (POST) ==="
# Ask for several ids in one round trip. Replace these with ids from a list call.
curl -s "${AUTH[@]}" -H "Content-Type: application/json" \
  -X POST "$BASE/features/details/batch" \
  -d '{"ids":["ON-cam-155","ON-cam-1434"]}' | python3 -m json.tool | head -30

echo ""
echo "=== Cursor pagination: page 1, then follow next_cursor ==="
# offset is capped (and the cap drops to 10,000 on 2026-10-06); a cursor has no
# ceiling and does not slow down as you go deeper.
PAGE1=$(curl -s "${AUTH[@]}" "$BASE/features?type=bridge_clearances&jurisdiction=TX&limit=5")
echo "$PAGE1" | python3 -m json.tool | head -12
CURSOR=$(echo "$PAGE1" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("next_cursor",""))')
if [ -n "$CURSOR" ]; then
  echo "--- page 2 ---"
  curl -s "${AUTH[@]}" "$BASE/features?type=bridge_clearances&jurisdiction=TX&limit=5&cursor=$CURSOR" \
    | python3 -m json.tool | head -12
fi

echo ""
echo "=== Public map tier — works with no API key at all ==="
curl -s "$BASE/map/config" | python3 -m json.tool
curl -s "$BASE/map/features?type=cameras&jurisdiction=ON&limit=3" | python3 -m json.tool | head -20
