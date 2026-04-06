/**
 * Road511 API — JavaScript features example (Node.js 18+)
 * Fetch cameras, signs, and weather stations near a location.
 *
 * Sign up at https://portal.road511.com for a free API key
 *
 * Usage:
 *   export ROAD511_API_KEY="sk_live_..."
 *   node javascript_features.mjs
 */

const BASE_URL = "https://api.road511.com/api/v1";
const API_KEY = process.env.ROAD511_API_KEY;
if (!API_KEY) {
  console.error("Set ROAD511_API_KEY environment variable");
  process.exit(1);
}

async function fetchFeatures(params) {
  const url = new URL(`${BASE_URL}/features`);
  for (const [key, val] of Object.entries(params)) {
    url.searchParams.set(key, val);
  }

  const resp = await fetch(url, {
    headers: { "X-API-Key": API_KEY },
  });

  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`HTTP ${resp.status}: ${body}`);
  }
  return resp.json();
}

// --- Example 1: Traffic cameras near Denver ---
console.log("=== Traffic cameras near Denver, CO ===");
const cameras = await fetchFeatures({
  type: "cameras",
  lat: 39.74,
  lng: -104.99,
  radius_km: 50,
  limit: 5,
});
console.log(`Found ${cameras.total} cameras within 50km`);
for (const cam of cameras.data) {
  const img = cam.properties?.image_url || "no image";
  console.log(`  ${cam.name} — ${img}`);
}

// --- Example 2: DMS signs in New York ---
console.log("\n=== Dynamic message signs in NY ===");
const signs = await fetchFeatures({
  type: "signs",
  jurisdiction: "NY",
  limit: 5,
});
console.log(`Found ${signs.total} signs`);
for (const sign of signs.data) {
  const msg = sign.properties?.message || "blank";
  console.log(`  ${sign.name}: "${msg}"`);
}

// --- Example 3: Weather stations in Montana ---
console.log("\n=== RWIS weather stations in MT ===");
const weather = await fetchFeatures({
  type: "weather_stations",
  jurisdiction: "MT",
  limit: 5,
});
console.log(`Found ${weather.total} weather stations`);
for (const ws of weather.data) {
  const temp = ws.properties?.temperature;
  const road = ws.properties?.road_surface;
  console.log(
    `  ${ws.name}: ${temp != null ? temp + "°F" : "N/A"}, surface: ${road || "N/A"}`
  );
}

// --- Example 4: Feature detail (lazy-loaded) ---
if (cameras.data.length > 0) {
  const id = cameras.data[0].id;
  console.log(`\n=== Detail for camera ${id} ===`);
  const resp = await fetch(`${BASE_URL}/features/${id}/details`, {
    headers: { "X-API-Key": API_KEY },
  });
  if (resp.ok) {
    const detail = await resp.json();
    console.log(`  Name: ${detail.name}`);
    console.log(`  Properties:`, JSON.stringify(detail.properties, null, 2).slice(0, 300));
  }
}

// --- Example 5: All feature types available ---
console.log("\n=== Available feature types ===");
const types = await fetch(`${BASE_URL}/features/types`, {
  headers: { "X-API-Key": API_KEY },
}).then((r) => r.json());
for (const t of types) {
  console.log(`  ${t.type}: ${t.count} features`);
}
