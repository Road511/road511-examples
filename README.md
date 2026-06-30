# Road511 API Examples

Code examples for the [Road511 Traffic Data API](https://road511.com) — real-time traffic events, cameras, signs, bridge clearances, weight restrictions, and truck routes across 65 US and Canadian jurisdictions.

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
| [examples/javascript_features.mjs](examples/javascript_features.mjs) | JavaScript | Fetch cameras, signs, weather stations near a location |
| [examples/go_geojson.go](examples/go_geojson.go) | Go | Stream events as GeoJSON and save to file |
| [postman/road511.postman_collection.json](postman/road511.postman_collection.json) | Postman | Full collection — import into Postman |

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
| `GET /events/geojson` | Same data as GeoJSON FeatureCollection |
| `GET /events/{id}` | Single event by ID |
| `GET /features?type=cameras` | Traffic cameras with image URLs |
| `GET /features?type=signs` | Dynamic message sign content |
| `GET /features?type=weather_stations` | RWIS weather station readings |
| `GET /features?type=rest_areas` | Rest areas, truck parking |
| `GET /features?type=bridge_clearances` | Bridge clearances (621K from NBI) |
| `GET /features?type=weight_restrictions` | Weight-posted roads and bridges |
| `GET /features?type=truck_routes` | STAA truck routes (FHWA) |
| `GET /features?type=ev_charging` | EV charging stations (NREL) |
| `GET /features/geojson` | Features as GeoJSON |
| `GET /features/{id}/details` | Full detail for a single feature |
| `GET /truck/corridor` | All truck restrictions along a route corridor |
| `GET /jurisdictions` | List of 65 supported jurisdictions |
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
| `offset` | `50` | Pagination offset |

## Data Coverage

- **65 jurisdictions** — all 50 US states + 13 Canadian provinces/territories + DC + SF Bay
- **Traffic events** — incidents, construction, closures, weather advisories, lane restrictions
- **28+ feature types** — cameras, signs, weather stations, rest areas, EV charging, bridges, truck routes, weight restrictions, and more
- **Updated every 1-5 minutes** depending on source

## Links

- [Landing page](https://road511.com) — overview and pricing
- [API Documentation](https://road511.com/docs.html) — full endpoint reference with examples
- [Interactive Map](https://map.road511.com) — live traffic map demo
- [Developer Portal](https://portal.road511.com) — sign up, manage API keys, view usage
- [Swagger UI](https://api.road511.com/api/v1/docs/) — interactive API explorer

## License

These examples are MIT licensed. The Road511 API itself requires an API key — see [pricing](https://road511.com/#pricing).
