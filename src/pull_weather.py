"""
Pull historical daily weather from Open-Meteo (JSON approach) for ALL regions.
Run from the PROJECT ROOT:  python -m src.pull_weather
Data source: Open-Meteo Historical Weather API (/v1/archive).
Licence: free API non-commercial use; data CC BY 4.0.
Saves both raw JSON (provenance) and a CSV (working format) per region.
"""
import json
import requests
import pandas as pd
from datetime import date

from config import REGIONS, WEATHER_VARIABLES, WEATHER_START_DATE, WEATHER_DIR

url = "https://archive-api.open-meteo.com/v1/archive"

# Make the output folder once, before the loop
WEATHER_DIR.mkdir(parents=True, exist_ok=True)

# --- Loop over every region defined in config.py ---
for region_key, region in REGIONS.items():
    print(f"\nRequesting weather for {region['name']} ({region_key})...")

    params = {
        "latitude": region["lat"],
        "longitude": region["lon"],
        "start_date": WEATHER_START_DATE,
        "end_date": date.today().isoformat(),
        "daily": WEATHER_VARIABLES,
        "timezone": "Pacific/Auckland",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    # Save raw JSON (provenance)
    json_path = WEATHER_DIR / f"weather_{region_key}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved raw JSON to {json_path}")

    # Convert daily block to a table and save CSV
    daily = pd.DataFrame(data["daily"])
    print(f"  Received {len(daily)} days of data.")

    csv_path = WEATHER_DIR / f"weather_{region_key}.csv"
    daily.to_csv(csv_path, index=False)
    print(f"  Saved CSV to {csv_path}")

print("\nAll regions done.")