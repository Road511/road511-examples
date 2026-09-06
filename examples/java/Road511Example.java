// Road511 API — Java example (JDK 11+, no dependencies)
//
// Java is the largest consumer of this API by request volume, so this example
// stays on the JDK's own HttpClient rather than pulling in OkHttp or Jackson:
// it should run anywhere with a JDK and nothing else installed.
//
// Usage:
//
//   export ROAD511_API_KEY="YOUR_API_KEY"
//   java examples/java/Road511Example.java
//
// (JDK 11+ runs a single .java file directly — no javac step needed.)

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;

public class Road511Example {

    private static final String BASE_URL = "https://api.road511.com/api/v1";
    private static final HttpClient CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(15))
            .build();

    private static String apiKey;

    public static void main(String[] args) throws Exception {
        apiKey = System.getenv("ROAD511_API_KEY");
        if (apiKey == null || apiKey.isBlank()) {
            System.err.println("Set ROAD511_API_KEY environment variable");
            System.exit(1);
        }

        events();
        featureDetail();
        cursorWalk();
        publicMapTier();
    }

    // --- Traffic events with filters ---
    private static void events() throws Exception {
        System.out.println("=== Active incidents in WA ===");
        String body = get("/events", params("jurisdiction", "WA", "type", "incident", "limit", "5"));
        for (String title : extractAll(body, "\"title\":\"")) {
            System.out.println("  " + title);
        }
    }

    // --- has_details, then the detail call it points at ---
    private static void featureDetail() throws Exception {
        System.out.println("\n=== Camera detail ===");
        String list = get("/features", params("type", "cameras", "jurisdiction", "ON", "limit", "1"));
        String id = extract(list, "\"id\":\"");
        if (id == null) {
            System.out.println("  no rows returned");
            return;
        }
        // Rows advertise extra data with has_details; fetch it on demand.
        String detail = get("/features/" + encodePathSegment(id) + "/details", Map.of());
        System.out.println("  " + id + " cache=" + extract(detail, "\"cache\":\""));
        String image = extract(detail, "\"image_url\":\"");
        if (image != null) {
            System.out.println("  image_url=" + image);
        }
    }

    // --- Cursor pagination: the way to read a set larger than the offset cap ---
    private static void cursorWalk() throws Exception {
        System.out.println("\n=== Cursor paging: bridge clearances in TX ===");
        String cursor = null;
        int pages = 0, rows = 0;

        while (pages < 3) { // raise or drop this bound to walk the whole set
            Map<String, String> p = params(
                    "type", "bridge_clearances", "jurisdiction", "TX", "limit", "100");
            // Never send offset alongside cursor — that combination is a 400.
            if (cursor != null) {
                p.put("cursor", cursor);
            }
            String body = get("/features", p);
            pages++;
            rows += countOf(body, "\"id\":\"");

            // Stop when has_more is false; next_cursor is absent on that page.
            if (!body.contains("\"has_more\":true")) {
                break;
            }
            cursor = extract(body, "\"next_cursor\":\"");
            if (cursor == null) {
                break;
            }
        }
        System.out.println("  read " + rows + " rows over " + pages + " pages");
    }

    // ---------- plumbing ----------

    private static String get(String path, Map<String, String> params) throws Exception {
        StringBuilder url = new StringBuilder(BASE_URL).append(path);
        if (!params.isEmpty()) {
            url.append('?');
            boolean first = true;
            for (Map.Entry<String, String> e : params.entrySet()) {
                if (!first) {
                    url.append('&');
                }
                url.append(URLEncoder.encode(e.getKey(), StandardCharsets.UTF_8))
                   .append('=')
                   .append(URLEncoder.encode(e.getValue(), StandardCharsets.UTF_8));
                first = false;
            }
        }
        HttpRequest req = HttpRequest.newBuilder()
                .uri(URI.create(url.toString()))
                .header("X-API-Key", apiKey)
                .timeout(Duration.ofSeconds(30))
                .GET()
                .build();
        HttpResponse<String> resp = CLIENT.send(req, HttpResponse.BodyHandlers.ofString());
        if (resp.statusCode() != 200) {
            throw new IllegalStateException("HTTP " + resp.statusCode() + " on " + path + ": " + resp.body());
        }
        return resp.body();
    }

    // URLEncoder is form encoding, not path encoding: it turns a space into "+",
    // which inside a path segment means a literal plus. 33,052 feature ids
    // contain a space and 191 contain a slash, so this matters in practice.
    private static String encodePathSegment(String s) {
        return URLEncoder.encode(s, StandardCharsets.UTF_8).replace("+", "%20");
    }

    private static Map<String, String> params(String... kv) {
        Map<String, String> m = new LinkedHashMap<>();
        for (int i = 0; i + 1 < kv.length; i += 2) {
            m.put(kv[i], kv[i + 1]);
        }
        return m;
    }

    // Deliberately crude string probing rather than a JSON dependency — this
    // file is meant to run with nothing installed. Use Jackson or Gson in
    // anything real; every response here is ordinary JSON.
    private static String extract(String json, String key) {
        int i = json.indexOf(key);
        if (i < 0) {
            return null;
        }
        int start = i + key.length();
        int end = json.indexOf('"', start);
        return end < 0 ? null : json.substring(start, end);
    }

    private static java.util.List<String> extractAll(String json, String key) {
        java.util.List<String> out = new java.util.ArrayList<>();
        int i = 0;
        while ((i = json.indexOf(key, i)) >= 0) {
            int start = i + key.length();
            int end = json.indexOf('"', start);
            if (end < 0) {
                break;
            }
            out.add(json.substring(start, end));
            i = end;
        }
        return out;
    }

    private static int countOf(String haystack, String needle) {
        int n = 0, i = 0;
        while ((i = haystack.indexOf(needle, i)) >= 0) {
            n++;
            i += needle.length();
        }
        return n;
    }
}
