/**
 * Road511 API — groups, and the filters that trim a response
 * Sign up at https://portal.road511.com for a free API key
 *
 * Two taxonomies save you from hardcoding lists that drift:
 *   /features/groups      feature types bundled by purpose (imagery, trucking, weather...)
 *   /jurisdictions/groups jurisdictions bundled by state (CA = CA + WZDX_CA + 511SF)
 *
 * Both are worth calling once at startup rather than pinning their contents in
 * your own code — new types and new feeds land in them without an API change.
 *
 * Usage:
 *   export ROAD511_API_KEY="YOUR_API_KEY"
 *   node javascript_groups.mjs
 */

const BASE_URL = "https://api.road511.com/api/v1";
const API_KEY = process.env.ROAD511_API_KEY;
if (!API_KEY) {
  console.error("Set ROAD511_API_KEY environment variable");
  process.exit(1);
}

async function api(path, params = {}) {
  const url = new URL(`${BASE_URL}${path}`);
  for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const resp = await fetch(url, { headers: { "X-API-Key": API_KEY } });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${await resp.text()}`);
  return resp.json();
}

// --- Feature groups ---
console.log("=== Feature groups ===");
const featureGroups = await api("/features/groups");
for (const g of featureGroups) {
  console.log(`  ${g.id.padEnd(14)} ${g.name} — ${g.feature_types.length} types`);
}

// --- Query a whole group in one call ---
// `group=` expands to every type in it, so you do not enumerate them yourself.
// Note the one restriction: combined with radius_km the radius is capped at
// 200 km, because a wider search across every type in a group cannot be served
// in time. Query a single `type` when you need an unrestricted radius.
console.log("\n=== Everything in the 'trucking' group near Chicago ===");
const trucking = await api("/features", {
  group: "trucking",
  lat: 41.88,
  lng: -87.63,
  radius_km: 50,
  limit: 10,
});
const byType = {};
for (const row of trucking.data) byType[row.feature_type] = (byType[row.feature_type] ?? 0) + 1;
console.log(`  ${trucking.total} matching, this page covers:`, byType);

// --- Jurisdiction groups ---
// Querying a state's primary code auto-expands to its whole group, so
// jurisdiction=CA already includes WZDX_CA and 511SF. This endpoint shows what
// any given code will expand into.
console.log("\n=== Jurisdiction groups ===");
const jurGroups = await api("/jurisdictions/groups");
for (const g of jurGroups.slice(0, 5)) {
  console.log(`  ${g.primary_jurisdiction_code.padEnd(4)} ${g.name} -> ${g.members.join(", ")}`);
}

// --- active: lifecycle, not open/closed ---
// `is_active` false means the source stopped listing that row, not that a
// facility is shut. Reading historical rows is an analytics-tier feature; on
// other plans the query is clamped to active-only whatever you ask for.
console.log("\n=== active filter ===");
const activeOnly = await api("/features", { type: "cameras", jurisdiction: "ON", active: "true", limit: 1 });
console.log(`  active cameras in ON: ${activeOnly.total}`);

// --- has_details: what the list row is NOT telling you ---
// Rows are lean on purpose. Where the source publishes more than the list
// carries, the row says so and the detail endpoint fetches it on demand.
console.log("\n=== has_details ===");
const sample = await api("/features", { type: "cameras", jurisdiction: "ON", limit: 5 });
const withDetail = sample.data.filter((r) => r.has_details);
console.log(`  ${withDetail.length} of ${sample.data.length} rows carry extra detail`);
if (withDetail.length) {
  const detail = await api(`/features/${encodeURIComponent(withDetail[0].id)}/details`);
  console.log(`  ${withDetail[0].id}: cache=${detail.cache}`);
}
