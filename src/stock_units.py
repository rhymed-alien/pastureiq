"""
stock_units.py — PastureIQ Group A (feed demand) + Group C2 Signal 2 (stocking_ratio).

FEED-ONLY. Terrain does NOT belong in LSU values — an animal's feed need doesn't change by
region. Regional/terrain differences live in carrying capacity
(data/raw/reference/terrain_carrying_capacity.csv), consumed here only by stocking_ratio().

Source: B+LNZ Sheep & Beef Farm Survey standard conversions, loaded from
data/raw/reference/lsu_conversion_table.csv (the CSV is the source of truth — NOT a hardcoded
dict, consistent with terrain_carrying_capacity.csv and pasture_growth_curve.csv). Baseline:
1 LSU = 6000 MJME/year = 520 kg DM/year (modern NZ standard ewe). Source: RuralHQ (2019);
Otago Regional Council memo (2023) citing Parker (1998).

⚠ CAVEAT (per B+LNZ): these are a general guide for policy-level implied feed utilisation,
NOT a substitute for farm-level feed budgeting. Figures are currently UNDER REVIEW by B+LNZ
(held constant for years to preserve a consistent timeseries).
"""

import csv
from config import DM_PER_LSU_PER_DAY
#DM_PER_LSU_PER_DAY = 1.42  520 kg DM/yr / 365 (annual average; seasonal refinement later)

LSU_TABLE_PATH = "data/raw/reference/lsu_conversion_table.csv"
TERRAIN_CAPACITY_PATH = "data/raw/reference/terrain_carrying_capacity.csv"


def _load_lsu_table(path=LSU_TABLE_PATH):
    """
    Loads lsu_conversion_table.csv into {animal_class: stock_units (float)}.

    ⚠ Reads the 'stock_units' column only. Does NOT use 'cattle_equivalent' — that's a
    within-cattle relative ratio (e.g. weaner vs MA cow), not a feed-demand figure. Using it
    here would silently produce wrong feed totals.

    Adds 'lamb' as an interim entry (Open Decision #4, resolved-interim): B+LNZ's survey has
    no standalone lamb class, so lamb is set equal to whatever 'grazing_sheep' resolves to at
    load time — nearest survey class, not a hardcoded guess. If B+LNZ later supplies a real
    lamb figure, add an actual 'lamb' row to the CSV and this fallback stops applying
    automatically (the CSV row would be read directly instead).
    """
    values = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            values[row["animal_class"]] = float(row["stock_units"])

    if "lamb" not in values:
        if "grazing_sheep" not in values:
            raise KeyError(
                "Cannot set the interim 'lamb' LSU fallback — 'grazing_sheep' is missing from "
                f"{path}. Add it back, or add a real 'lamb' row instead."
            )
        values["lamb"] = values["grazing_sheep"]

    return values


LSU_VALUES = _load_lsu_table()


def calculate_total_lsu(stock_dict):
    """
    stock_dict: {class_name: head_count, ...} e.g. {"ewe": 200, "ma_cow": 15}
    Returns total LSU (float). Raises KeyError with a clear message if a class isn't in
    LSU_VALUES, rather than silently skipping it.
    """
    total = 0.0
    for class_name, count in stock_dict.items():
        if class_name not in LSU_VALUES:
            raise KeyError(
                f"'{class_name}' is not in LSU_VALUES. Check spelling against the keys in "
                f"stock_units.LSU_VALUES, or add it (with a cited source) if it's a genuinely "
                f"new class."
            )
        total += count * LSU_VALUES[class_name]
    return total


def daily_feed_demand_kgDM(total_lsu):
    """total_lsu × 1.42 kg DM/day/LSU (annual average; see Group A caveat on seasonality)."""
    return total_lsu * DM_PER_LSU_PER_DAY


def _load_terrain_capacity(path=TERRAIN_CAPACITY_PATH):
    """Loads terrain_carrying_capacity.csv into a dict keyed by terrain_type."""
    capacity = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            capacity[row["terrain_type"]] = row
    return capacity


def stocking_ratio(total_lsu, effective_hectares, terrain_type, capacity_table=None):
    """
    Group C2 Signal 2 — structural baseline, no cover or weather needed.

    stocking_ratio = (total_LSU / effective_hectares) / carrying_capacity_SU_per_ha
        > 1  → stocked beyond land-class typical capacity (overstocked)
        < 1  → room to add (understocked)

    carrying_capacity_SU_per_ha is the MIDPOINT of the terrain's min/max range from
    terrain_carrying_capacity.csv. ⚠ DECISION MADE HERE (not previously specified in
    FORMULAS.md): using the midpoint rather than min or max, since a range doesn't collapse to
    one number without a choice, and midpoint avoids systematically biasing the ratio toward
    "overstocked" (if max were used) or "understocked" (if min were used). Revisit if farmer
    validation suggests midpoint doesn't match real-world judgement.

    Raises ValueError (does not silently guess) if:
      - terrain_type isn't in the capacity table at all, or
      - the table row is missing min/max data (e.g. "lifestyle_flat" or "high_country" —
        see terrain_carrying_capacity.csv notes column for why).

    ⚠ UNIT CHECK: assumes SU and LSU are the same ewe-equivalent basis (FORMULAS.md Open
    Decision #6 — not yet formally confirmed).
    """
    if capacity_table is None:
        capacity_table = _load_terrain_capacity()

    if terrain_type not in capacity_table:
        raise ValueError(
            f"'{terrain_type}' not found in terrain_carrying_capacity.csv. "
            f"Known terrain types: {list(capacity_table.keys())}"
        )

    row = capacity_table[terrain_type]
    min_su, max_su = row["min_su_per_ha"], row["max_su_per_ha"]

    if min_su in ("", None) or max_su in ("", None):
        raise ValueError(
            f"terrain_type '{terrain_type}' has an incomplete SU/ha range in "
            f"terrain_carrying_capacity.csv (min='{min_su}', max='{max_su}'). "
            f"See that file's notes column — this terrain type is not yet sourced. "
            f"stocking_ratio cannot be computed until it is."
        )

    carrying_capacity_su_per_ha = (float(min_su) + float(max_su)) / 2
    return (total_lsu / effective_hectares) / carrying_capacity_su_per_ha

