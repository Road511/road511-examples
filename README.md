# Road511 API Examples

Code examples for the [Road511 Traffic Data API](https://road511.com) — real-time traffic events, cameras, signs, bridge clearances, weight restrictions, and truck routes across US states and Canadian provinces.

## Quick Start

1. [Sign up for a free API key](https://portal.road511.com/) (14-day trial, no credit card)
2. Set your key as an environment variable:
   ```bash
   export ROAD511_API_KEY="YOUR_API_KEY"
   ```
3. Run any example below

## Examples

| File | Language | Description |
|------|----------|-------------|
| [examples/curl.sh](examples/curl.sh) | curl | All major endpoints in one script |
| [examples/python_events.py](examples/python_events.py) | Python | Query traffic events with filters |
| [examples/python_truck_corridor.py](examples/python_truck_corridor.py) | Python | Truck corridor — bridges, weight limits, restrictions along a route |
| [examples/python_features_paging.py](examples/python_features_paging.py) | Python | Read a whole feature set with cursor pagination |
| [examples/python_feature_details.py](examples/python_feature_details.py) | Python | `has_details` → single and batched detail fetch |
| [examples/python_scheduled_windows.py](examples/python_scheduled_windows.py) | Python | Planned work by date — the scheduled-window filters |
| [examples/python_analytics.py](examples/python_analytics.py) | Python | Every analytics endpoint (Pro+ plan) |
| [examples/javascript_groups.mjs](examples/javascript_groups.mjs) | JavaScript | Feature and jurisdiction groups, `active`, `has_details` |
| [examples/javascript_routing.mjs](examples/javascript_routing.mjs) | JavaScript | Truck routing, quota, saved routes |
| [examples/java/Road511Example.java](examples/java/Road511Example.java) | Java | Events, detail, cursor paging — JDK 11+, no dependencies |
| [examples/javascript_features.mjs](examples/javascript_features.mjs) | JavaScript | Fetch cameras, signs, weather stations near a location |
| [examples/go_geojson.go](examples/go_geojson.go) | Go | Stream events as GeoJSON and save to file |
| [postman/road511.postman_collection.json](postman/road511.postman_collection.json) | Postman | Core read endpoints — import into Postman |

Between them these examples cover the keyed API — every endpoint you get with an
API key. Coverage is collective, not per file: each example is task-shaped and
shows the endpoints that need explanation rather than one call each, so no single
file is a complete tour. `curl.sh` is the broadest single starting point, and the
Postman collection covers the core read endpoints.

## API Overview

**Base URL:** `https://api.road511.com/api/v1`

**Authentication:** Pass your API key via header or query param:
```
X-API-Key: YOUR_API_KEY
```
or
```
?api_key=YOUR_API_KEY
```

### Core Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /events` | Traffic incidents, closures, construction, weather advisories |
| `GET /events/geojson` | Same data as GeoJSON FeatureCollection (Starter+ plan) |
| `GET /events/{id}` | Single event by ID |
| `GET /features?type=cameras` | Traffic cameras with image URLs |
| `GET /features?type=signs` | Dynamic message sign content |
| `GET /features?type=weather_stations` | RWIS weather station readings |
| `GET /features?type=rest_areas` | Rest areas. Truck parking is a separate type — `truck_parking` |
| `GET /features?type=bridge_clearances` | Bridge clearances (from the FHWA National Bridge Inventory) |
| `GET /features?type=weight_restrictions` | Weight-posted roads and bridges |
| `GET /features?type=truck_routes` | STAA truck routes (FHWA) |
| `GET /features?type=ev_charging` | EV charging stations (NREL) |
| `GET /features/geojson` | Features as GeoJSON (Starter+ plan) |
| `GET /features/{id}/details` | Full detail for a single feature |
| `GET /truck/corridor` | All truck restrictions along a route corridor (Pro+ plan) |
| `GET /jurisdictions` | Every supported jurisdiction — call it for the current list |
| `GET /stats` | Active event and feature counts |

### Common Query Parameters

| Parameter | Example | Description |
|-----------|---------|-------------|
| `jurisdiction` | `CA` | Filter by US state or Canadian province code |
| `type` | `incident` | Event type: incident, construction, closure, special_event, etc. |
| `severity` | `major` | Severity: critical, major, moderate, minor |
| `bbox` | `-124,32,-114,42` | Bounding box (west,south,east,north) |
| `lat` + `lng` + `radius_km` | `47.6,-122.3,50` | Radius search |
| `road` | `I-95` | Filter by road name |
| `limit` | `100` | Results per page (default 100, capped by plan) |
| `offset` | `50` | Pagination offset. Capped — see Pagination below |
| `cursor` | `MjAyNi0wOS0w...` | Keyset pagination on `/features`. Pass back the `next_cursor` from the previous response |

## Pagination

Two ways to page, and the choice matters once a result set gets large.

**`offset`** works on every list endpoint and is right for shallow paging —
first few pages, or a jump-to-page-N in a UI. Its cost grows with depth, because
the database counts past every row it skips, and it is capped: requests above
the ceiling are rejected with 400.

⚠️ **The offset ceiling is 50,000 today and drops to 10,000 on 2026-10-06.**

**`cursor`** is keyset pagination on `/features`. Every response with a next page
carries `next_cursor`; send it back as `cursor` to get the following page. It has
no ceiling and its cost does not grow with depth, so it is the only way to read a
feature set larger than the cap — and several single `type` + `jurisdiction` sets
are larger than it.

```
GET /features?type=cameras&jurisdiction=TX&limit=100
  -> { "data": [...], "has_more": true, "next_cursor": "MjAyNi0wOS0w..." }

GET /features?type=cameras&jurisdiction=TX&limit=100&cursor=MjAyNi0wOS0w...
```

Rules: never send `cursor` and `offset` together (400); stop when `has_more` is
false, where `next_cursor` is absent; treat the cursor as opaque and echo it back
unchanged. `/events` has no cursor — page it with `offset`.

Worked example: [examples/python_features_paging.py](examples/python_features_paging.py).

## Data Coverage

Coverage grows continuously, so this file deliberately quotes no counts — they
would be wrong within weeks. Ask the API instead; both endpoints are public and
need no key:

```bash
curl -s https://api.road511.com/api/v1/jurisdictions | jq 'length'   # jurisdictions covered
curl -s https://api.road511.com/api/v1/stats                         # live event + feature counts
curl -s https://api.road511.com/api/v1/features/types                # every feature type available
```

- **Jurisdictions** — US states, Canadian provinces and territories, plus regional and municipal feeds
- **Traffic events** — incidents, construction, closures, weather advisories, lane restrictions
- **Feature types** — cameras, signs, weather stations, rest areas, truck parking, EV charging, bridge clearances, truck routes, weight restrictions, and many more
- **Updated every 1-5 minutes** depending on source

## Links

- [Landing page](https://road511.com) — overview and pricing
- [API Documentation](https://road511.com/docs.html) — full endpoint reference with examples
- [Interactive Map](https://map.road511.com) — live traffic map demo
- [Developer Portal](https://portal.road511.com) — sign up, manage API keys, view usage
- [API reference](https://road511.com/reference.html) — interactive explorer, generated from the OpenAPI spec

## License

These examples are MIT licensed. The Road511 API itself requires an API key — see [pricing](https://road511.com/#pricing).
