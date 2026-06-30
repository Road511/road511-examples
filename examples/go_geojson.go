// Road511 API — Go GeoJSON example
// Fetch traffic events as GeoJSON and save to a file.
//
// Sign up at https://portal.road511.com for a free API key (Starter+ for GeoJSON)
//
// Usage:
//
//	export ROAD511_API_KEY="YOUR_API_KEY"
//	go run go_geojson.go
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
)

const baseURL = "https://api.road511.com/api/v1"

func main() {
	apiKey := os.Getenv("ROAD511_API_KEY")
	if apiKey == "" {
		fmt.Fprintln(os.Stderr, "Set ROAD511_API_KEY environment variable")
		os.Exit(1)
	}

	// --- Example 1: Events GeoJSON for California ---
	fmt.Println("=== Fetching CA events as GeoJSON ===")
	geojson, err := fetchGeoJSON(apiKey, "/events/geojson", url.Values{
		"jurisdiction": {"CA"},
		"limit":        {"100"},
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	// Save to file
	outFile := "ca_events.geojson"
	if err := os.WriteFile(outFile, geojson, 0644); err != nil {
		fmt.Fprintf(os.Stderr, "Write error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("  Saved to %s (%d bytes)\n", outFile, len(geojson))

	// Parse and count features
	var fc struct {
		Type     string `json:"type"`
		Features []json.RawMessage `json:"features"`
	}
	if err := json.Unmarshal(geojson, &fc); err == nil {
		fmt.Printf("  Type: %s, Features: %d\n", fc.Type, len(fc.Features))
	}

	// --- Example 2: Features GeoJSON — cameras in Washington ---
	fmt.Println("\n=== Fetching WA cameras as GeoJSON ===")
	geojson, err = fetchGeoJSON(apiKey, "/features/geojson", url.Values{
		"type":         {"cameras"},
		"jurisdiction": {"WA"},
		"limit":        {"50"},
	})
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}

	outFile = "wa_cameras.geojson"
	if err := os.WriteFile(outFile, geojson, 0644); err != nil {
		fmt.Fprintf(os.Stderr, "Write error: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("  Saved to %s (%d bytes)\n", outFile, len(geojson))

	if err := json.Unmarshal(geojson, &fc); err == nil {
		fmt.Printf("  Type: %s, Features: %d\n", fc.Type, len(fc.Features))
	}

	fmt.Println("\nOpen these .geojson files in https://geojson.io to visualize on a map.")
}

func fetchGeoJSON(apiKey, endpoint string, params url.Values) ([]byte, error) {
	u := baseURL + endpoint + "?" + params.Encode()

	req, err := http.NewRequest("GET", u, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("X-API-Key", apiKey)

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, string(body[:min(len(body), 200)]))
	}

	return body, nil
}
