#!/usr/bin/env python3
"""
Geo-Data Loader

Fetches all countries from restcountries.com and stores them as:
{
  "Syria": {
    "cca2": "SY",
    "region": "Asia",
    "borders": ["IQ", "IL", "JO", "LB", "TR"]
  },
  ...
}

Run:
    python geo_data_fetch.py
"""
import json
import logging
from pathlib import Path
import httpx

# Logging setup
LOG = logging.getLogger("geodata_loader")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API URL and output path (save to IP_Intelligence/app/geodata.json)
API_URL = "https://restcountries.com/v3.1/all?fields=name,cca2,cca3,region,borders"
OUTPUT_FILE = Path(__file__).parent / "app" / "geodata.json"

def fetch_data():
    """Fetch all countries from the API"""
    LOG.info("Fetching country data...")
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(API_URL)
        resp.raise_for_status()
        LOG.info("Data fetched successfully.")
        return resp.json()

def build_cca3_map(countries):
    """Build map for cca3 -> cca2 code conversion"""
    return {
        c.get("cca3"): c.get("cca2")
        for c in countries
        if c.get("cca3") and c.get("cca2")
    }

def process_data(countries):
    """Convert to the desired output structure"""
    LOG.info("Processing data...")

    cca3_to_cca2 = build_cca3_map(countries)
    formatted = {}

    for c in countries:
        name_obj = c.get("name", {})
        name = name_obj.get("common") if isinstance(name_obj, dict) else None
        cca2 = c.get("cca2")
        region = c.get("region", "Unknown")
        borders_cca3 = c.get("borders", [])

        if not name or not cca2:
            continue

        borders_cca2 = [
            cca3_to_cca2.get(b) for b in borders_cca3 if cca3_to_cca2.get(b)
        ]

        formatted[name] = {
            "cca2": cca2,
            "region": region,
            "borders": borders_cca2
        }

    LOG.info(f"Processed {len(formatted)} countries.")
    return formatted

def save_json(path, data):
    """Save processed data to JSON"""
    LOG.info(f"Saving data to {path}...")
    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    LOG.info("Data saved successfully.")

def main():
    countries = fetch_data()
    processed = process_data(countries)
    save_json(OUTPUT_FILE, processed)

if __name__ == "__main__":
    main()
