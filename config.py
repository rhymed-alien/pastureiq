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

# config.py additions — append to existing config.py
# Covers FORMULAS.md Group A constants, Group F confidence anchoring, Group C2 residual cover.

# --- Feed demand (Group A) ---
DM_PER_LSU_PER_YEAR = 520          # kg DM/year per stock unit (modern NZ standard ewe)
DM_PER_LSU_PER_DAY = 1.42          # 520 / 365 (annual average; seasonal refinement later)
MJME_PER_LSU_PER_YEAR = 6000       # energy-equivalent of 1 LSU
# Source: RuralHQ (2019); Otago Regional Council memo (2023) citing Parker (1998).

# --- Time windows & confidence (Group F) — anchored to measured forecast skill, not gut feel ---
TIME_WINDOWS_DAYS = [7, 14, 28]
CONFIDENCE_BY_HORIZON = {7: "HIGH", 14: "MEDIUM", 28: "LOW"}
WEATHER_CONFIDENCE = {7: 0.85, 14: 0.60, 28: 0.40}
# Source: American Meteorological Society (no useful daily skill beyond ~8 days);
# Riemer et al./JGU (14-day hard ceiling); Weather Company (~90% at 5d, ~80% at 7d);
# S2S hydropower study (4-week average precip retains fair skill).

# --- Pasture residual cover (Group C2) — TERRAIN lookup, NOT a single national figure ---
# ⚠ PLACEHOLDER — all four values still need sourcing (AgResearch/DairyNZ grazing-residual
# guidance by terrain class, or B+LNZ if held). DO NOT use this dict in calculate_days_of_feed
# until populated — None is deliberate, not a stand-in number, so a missing value fails loudly
# rather than silently computing a wrong countdown.
MIN_RESIDUAL_COVER_BY_TERRAIN = {
    "hard_hill": None,       # kg DM/ha — TBD
    "steep_hill": None,      # kg DM/ha — TBD
    "easier_hill": None,     # kg DM/ha — TBD
    "lifestyle_flat": None,  # kg DM/ha — TBD; West Auckland edge case, see note below
}
# NOTE: lifestyle_flat has no B+LNZ farm-class equivalent at all (B+LNZ classes are hill-country
# sheep/beef, not lifestyle blocks) — this may need a different source entirely, not just a
# missing number. Flagged in terrain_carrying_capacity.csv build note.