// Road511 API — the public map endpoints, no API key required
//
// Everything under /map/* is open: no key, no signup. It is the compact twin of
// the keyed API, meant for drawing a map — type-specific properties are stripped
// (cameras excepted, because stream URLs are the whole point of a camera pin).
//
// Restrictions that come with being keyless: at most 100 results per call, 60
// requests per minute per IP, and no pagination — offset is forced to 0. Use the
// keyed /features and /events when you need the full row or a full set.
//
// Usage:
//
//	go run go_map_public.go
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"time"
)

const baseURL = "https://api.road511.com/api/v1"

var client = &http.Client{Timeout: 30 * time.Second}

// get fetches a public map endpoint. Note the absence of any auth header --
// that is the point of these routes.
func get(path string, params url.Values) ([]byte, error) {
	u := baseURL + path
	if len(params) > 0 {
		u += "?" + params.Encode()
	}
	resp, err := client.Get(u)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP %d on %s: %.200s", resp.StatusCode, path, body)
	}
	return body, nil
}

func must(path string, params url.Values) []byte {
	body, err := get(path, params)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
	return body
}

type listResponse struct {
	Data []struct {
		ID           string `json:"id"`
		Name         string `json:"name"`
		Title        string `json:"title"`
		Jurisdiction string `json:"jurisdiction"`
		FeatureType  string `json:"feature_type"`
		Type         string `json:"type"`
		Severity     string `json:"severity"`
		Latitude     float64
		Longitude    float64
	} `json:"data"`
	Total int `json:"total"`
}

func main() {
	// --- What the map tier allows ---
	fmt.Println("=== /map/config ===")
	var cfg struct {
		DetailLevel string `json:"detail_level"`
		MaxResults  int    `json:"max_results"`
		RPM         int    `json:"rpm"`
	}
	json.Unmarshal(must("/map/config", nil), &cfg)
	fmt.Printf("  detail=%s max_results=%d rpm=%d\n", cfg.DetailLevel, cfg.MaxResults, cfg.RPM)

	// --- Events on the map ---
	fmt.Println("\n=== /map/events (Ontario) ===")
	var events listResponse
	json.Unmarshal(must("/map/events", url.Values{"jurisdiction": {"ON"}, "limit": {"5"}}), &events)
	for _, e := range events.Data {
		fmt.Printf("  [%s] %s\n", e.Severity, e.Title)
	}

	// One event, compact. Same route the map popup uses.
	if len(events.Data) > 0 {
		id := events.Data[0].ID
		fmt.Printf("\n=== /map/events/%s ===\n", id)
		fmt.Printf("  %.200s\n", must("/map/events/"+url.PathEscape(id), nil))
	}

	// GeoJSON, ready to hand to Leaflet or MapLibre without reshaping.
	fmt.Println("\n=== /map/events/geojson ===")
	geo := must("/map/events/geojson", url.Values{"jurisdiction": {"ON"}, "limit": {"5"}})
	var fc struct {
		Type     string `json:"type"`
		Features []any  `json:"features"`
	}
	json.Unmarshal(geo, &fc)
	fmt.Printf("  %s with %d features\n", fc.Type, len(fc.Features))

	// --- Features on the map ---
	fmt.Println("\n=== /map/features/types ===")
	fmt.Printf("  %.240s\n", must("/map/features/types", nil))

	fmt.Println("\n=== /map/features (cameras in Ontario) ===")
	var features listResponse
	json.Unmarshal(must("/map/features", url.Values{
		"type": {"cameras"}, "jurisdiction": {"ON"}, "limit": {"5"},
	}), &features)
	for _, f := range features.Data {
		fmt.Printf("  %s — %s\n", f.ID, f.Name)
	}

	fmt.Println("\n=== /map/features/geojson ===")
	var fgeo struct {
		Type     string `json:"type"`
		Features []any  `json:"features"`
	}
	json.Unmarshal(must("/map/features/geojson", url.Values{
		"type": {"cameras"}, "jurisdiction": {"ON"}, "limit": {"5"},
	}), &fgeo)
	fmt.Printf("  %s with %d features\n", fgeo.Type, len(fgeo.Features))

	// Camera detail is the one type that stays full on the public tier, because
	// the stream URL is what a camera pin exists to show.
	if len(features.Data) > 0 {
		id := features.Data[0].ID
		fmt.Printf("\n=== /map/features/%s/details ===\n", id)
		fmt.Printf("  %.300s\n", must("/map/features/"+url.PathEscape(id)+"/details", nil))
	}
}
