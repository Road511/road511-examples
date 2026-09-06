/**
 * Road511 API — truck routing with hazard enrichment (Node.js 18+)
 * Sign up at https://portal.road511.com for a free API key
 *
 * /routing/route computes a truck-legal route and enriches it with what we hold
 * along the way: bridge clearances your trailer will not fit under, weight
 * postings, work zones, closures. Routing is metered separately from the data
 * API — every response carries a `quota` block, and /routing/quota reports the
 * same envelope without spending a call.
 *
 * Usage:
 *   export ROAD511_API_KEY="YOUR_API_KEY"
 *   node javascript_routing.mjs
 */

const BASE_URL = "https://api.road511.com/api/v1";
const API_KEY = process.env.ROAD511_API_KEY;
if (!API_KEY) {
  console.error("Set ROAD511_API_KEY environment variable");
  process.exit(1);
}

async function api(path, { method = "GET", body } = {}) {
  const resp = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      "X-API-Key": API_KEY,
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status} on ${path}: ${await resp.text()}`);
  return resp.json();
}

// --- Check the quota before spending it ---
// This call is free: it returns the same block a routing response carries.
console.log("=== Routing quota ===");
const quota = await api("/routing/quota");
console.log(`  plan=${quota.subscription?.plan} used=${quota.subscription?.used}/${quota.subscription?.limit}`);
console.log(`  remaining including top-ups: ${quota.total?.remaining}, resets ${quota.reset_at}`);

// --- Compute a route ---
// The truck block is what makes this different from a car router: the profile
// decides which roads are legal, and clearances are checked against your height.
console.log("\n=== Newark, NJ -> Baltimore, MD ===");
const route = await api("/routing/route", {
  method: "POST",
  body: {
    origin: { lat: 40.7357, lng: -74.1724 },
    destination: { lat: 39.2904, lng: -76.6122 },
    truck: {
      height_m: 4.11,      // 13'6" — the height most clearance warnings key on
      weight_t: 36.3,      // 80,000 lb
      axle_count: 5,
      commercial: true,
    },
    include: ["summary", "polyline"],
    enrichment: { min_severity: "moderate", buffer_m: 250 },
    units: "imperial",
    customer_route_id: "example-run-1",
  },
});

const first = route.routes?.[0];
console.log(`  route_id=${route.route_id} cached=${route.cached}`);
if (first?.summary) {
  const km = (first.summary.distance_m / 1000).toFixed(0);
  const hrs = (first.summary.duration_s / 3600).toFixed(1);
  console.log(`  ${km} km, ${hrs} h`);
  for (const toll of first.summary.toll_costs ?? []) {
    console.log(`  toll: ${toll.value} ${toll.currency}`);
  }
  // mileage_by_state is what IFTA reporting needs.
  for (const leg of (first.summary.mileage_by_state ?? []).slice(0, 5)) {
    console.log(`  mileage: ${JSON.stringify(leg)}`);
  }
}
// `ignored_fields` tells you which request fields the router did not apply —
// worth logging, because a silently dropped truck dimension is a safety issue.
if (route.ignored_fields?.length) {
  console.log(`  ignored_fields: ${route.ignored_fields.join(", ")}`);
}
if (route.toll_alternative) {
  console.log("  a toll-free alternative was also returned");
}

// --- Saved routes ---
// Every computed route is auto-saved for 30 minutes. Persisting one keeps it.
console.log("\n=== Recent saved routes ===");
const recent = await api("/routing/route/saved/recent");
for (const r of (recent.routes ?? []).slice(0, 5)) {
  console.log(`  ${r.id} persisted=${r.is_persisted} expires=${r.expires_at}`);
}

if (route.route_id) {
  console.log(`\n=== Points of interest along ${route.route_id} ===`);
  const pois = await api(`/routing/route/saved/${route.route_id}/features`);
  console.log(`  ${pois.count} features along the route`);
  for (const f of (pois.features ?? []).slice(0, 5)) {
    const km = (f.distance_along_route_m / 1000).toFixed(1);
    // available_spots is present only where the feed publishes live occupancy
    // (US TPIMS and several EU parking feeds). 0 means known full, not unknown.
    const spots = f.available_spots != null ? `, ${f.available_spots} spots free` : "";
    console.log(`  ${f.type.padEnd(16)} ${f.name ?? "(unnamed)"} — ${km} km in${spots}`);
  }
  // Note: detour_m and side are declared in the response schema but are
  // reserved for a future version and omitted today — do not build on them yet.

  // Refetch the saved route with its warnings re-evaluated against current data.
  const refetched = await api(`/routing/route/saved/${route.route_id}`);
  console.log(`  refetched: persisted=${refetched.is_persisted} expires=${refetched.expires_at}`);

  // Keep it past the 30-minute window.
  await api(`/routing/route/saved/${route.route_id}/persist`, { method: "POST" });
  console.log("  persisted");

  // ...and drop it when you are done. DELETE removes a saved route.
  await api(`/routing/route/saved/${route.route_id}`, { method: "DELETE" });
  console.log("  deleted");
}
