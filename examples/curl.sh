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
