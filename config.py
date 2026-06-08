"""
Central configuration for PastureIQ.
All paths, settings, and tunable values live here. Nothing else in the
codebase should hard-code a region, a file path, or a threshold — it
imports from here. This is what makes the project easy to extend or pivot.
"""
from pathlib import Path

# --- Project paths ---
ROOT = Path(__file__).parent
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
WEATHER_DIR = DATA_RAW / "weather"
MARKET_DIR = DATA_RAW / "market"
REFERENCE_DIR = DATA_RAW / "reference"
DB_PATH = ROOT / "pastureiq.sqlite"

# --- Target regions (coords used for weather pulls) ---
# To add, remove, or move a region, edit ONLY this dict. Everything downstream follows.
REGIONS = {
    "waikato":  {"name": "South Waikato / King Country",  "lat": -38.34, "lon": 175.16, "terrain": "steep_hill"},
    "taranaki": {"name": "South Taranaki / N. Whanganui",  "lat": -39.63, "lon": 174.93, "terrain": "steep_hill"},
    "auckland": {"name": "West Auckland lifestyle blocks",  "lat": -36.90, "lon": 174.52, "terrain": "hill"},
}

# --- Weather settings ---
WEATHER_START_DATE = "2015-01-01"
WEATHER_VARIABLES = [
    "temperature_2m_max", "temperature_2m_min", "precipitation_sum",
    "et0_fao_evapotranspiration", "windspeed_10m_max",
]

# --- Pasture pressure thresholds (tune as you learn) ---
PASTURE_RISK_GREEN_DAYS = 30   # more than this = comfortable
PASTURE_RISK_AMBER_DAYS = 14   # below this = act