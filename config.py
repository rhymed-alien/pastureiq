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
    "auckland": {"name": "West Auckland lifestyle blocks",  "lat": -36.90, "lon": 174.52, "terrain": "lifestyle_flat"},
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
# --- STOCK_CLASS_TO_PRICE_SERIES — append this to config.py ---
# Maps lsu_conversion_table.csv's feed-side classes to blnz_farmgate_prices.csv's
# market-side series. These are NOT the same taxonomy — a farmer's "ewe" mob sells as
# mutton, not as "ewe." No source document specifies this mapping directly; it's built
# from general NZ sheep/beef market knowledge and needs your confirmation, especially
# the entries flagged below. Draft, not verified fact — added 2026-07-17.
#
# CONFIDENT (standard NZ market classification, low ambiguity):
#   - Mature/cull breeding stock (ewe, ram, ma_cow, bull_breeding) sell at cull/mutton/
#     cow/bull prices, not premium young-stock prices.
#   - hogget -> mutton, NOT lamb: FORMULAS.md Group D already documents the lamb->hogget
#     age boundary as the point stock drops OUT of premium lamb pricing. This mapping is
#     just applying that documented rule, not introducing a new judgment call.
#
# NEEDS YOUR CONFIRMATION (real ambiguity, flagged inline below):
#   - wether: mapped to mutton assuming MATURE wethers. A young wether lamb would
#     actually be lamb-priced — this class doesn't distinguish age, so if your farm
#     mob's "wether" typically means young stock, this mapping is wrong for you.
#   - grazing_sheep: a generic/ambiguous LSU category (also used as the interim feed
#     proxy for "lamb" in stock_units.py — see Group A). For PRICE purposes it's
#     mapped to mutton as the best available generic match, but it's genuinely unclear
#     what this class represents on a real farm.
#   - *_weaner classes (heifer_weaner, bull_weaner, steer_weaner): mapped to the
#     closest available cattle price series, but those series are all pegged to a
#     270-295kg weight bracket — weaners are typically well under that weight. This is
#     a real, known weight-bracket mismatch, not a clean match. No weaner-specific
#     price series exists in blnz_farmgate_prices.csv currently.
#   - heifer_1.5yr, steer_1.5yr: same weight-bracket caveat, likely lighter than
#     270-295kg — mapped to the same series for lack of a better match.
#   - lamb: lsu_conversion_table.csv has NO standalone "lamb" row (Group A uses
#     grazing_sheep's LSU as an interim proxy — see stock_units.py). If your farm_mob
#     dict uses a "lamb" key for actual lambs, it needs a price mapping here even
#     though it has no feed-side LSU row of its own. Mapped to ym_lamb.
#
# OUT OF SCOPE, deliberately NOT mapped:
#   - r2_dairy_heifer, r1_dairy_heifer, dairy_cow_winter: dairy-origin grazing classes,
#     present in lsu_conversion_table.csv because dairy stock is sometimes grazed on
#     sheep/beef country under contract — not because PastureIQ prices dairy sales
#     (PROJECT_SPEC scopes this tool to sheep & beef farmers). Left unmapped on
#     purpose; get_price_signal_for_class() below returns None for these, same
#     graceful-degrade path as any other missing price data.

STOCK_CLASS_TO_PRICE_SERIES = {
    # Sheep
    "lamb": "ym_lamb",
    "hogget": "all_grades_mutton",
    "wether": "all_grades_mutton",          # ⚠ assumes mature wether
    "ram": "all_grades_mutton",
    "ewe": "all_grades_mutton",
    "grazing_sheep": "all_grades_mutton",   # ⚠ generic/ambiguous class

    # Beef
    "ma_cow": "m_cow_170_195kg",
    "heifer_2.5yr": "p_steer_heifer_270_295kg",
    "heifer_1.5yr": "p_steer_heifer_270_295kg",     # ⚠ likely lighter than bracket
    "heifer_weaner": "p_steer_heifer_270_295kg",    # ⚠ weaner weight well below bracket
    "bull_weaner": "m_bull_270_295kg",              # ⚠ weaner weight well below bracket
    "steer_weaner": "p_steer_heifer_270_295kg",     # ⚠ weaner weight well below bracket
    "steer_1.5yr": "p_steer_heifer_270_295kg",      # ⚠ likely lighter than bracket
    "steer_2.5yr": "p_steer_heifer_270_295kg",
    "bull_beef_1.5yr_plus": "m_bull_270_295kg",
    "bull_breeding": "m_bull_270_295kg",

    # Dairy-origin grazing classes — deliberately unmapped, out of scope (see above)
}