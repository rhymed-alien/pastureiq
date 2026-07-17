"""
pasture_model.py — Group B: PASTURE SUPPLY, plus Group C2 Signal 1 (flow balance)

Formulas: FORMULAS.md Group B / Group C2.
    growth_rate_kgdm_ha_day = seasonal_baseline(region, month) x water_surplus_adjustment
    daily_pasture_grown_kgDM = growth_rate_kgdm_ha_day x effective_hectares
    effective_hectares = total_hectares - non_grazeable_hectares
    net_daily_change_kgDM = daily_pasture_grown_kgDM - daily_feed_demand_kgDM   (Signal 1)

Data source: data/raw/reference/pasture_growth_curve.csv — rebuilt 2026-07-17 after a
fabricated DairyNZ citation was found and removed (see CHANGELOG.md). All three regions
now have real magnitude + real shape (Waikato/Auckland rescaled from real but imperfect
proxies; Taranaki direct). See DATA_SOURCES.md, Pasture Growth section, for full
per-region provenance and caveats — this module does not repeat them, only uses the
numbers.

NOT YET BUILT in this module (named gaps, do not silently fill):
- calculate_days_of_feed() / the absolute cover countdown — blocked on
  MIN_RESIDUAL_COVER_BY_TERRAIN, which is still all `None` in config.py (FORMULAS.md
  Group C2, Open Decision #2). Do not invent residual-cover figures to unblock this.
- classify_pasture_risk() (GREEN/AMBER/RED) — depends on calculate_days_of_feed(),
  same blocker.
- Water-surplus adjustment bounds (0.5-1.2) and the monthly-norm baseline are reasoned
  starting assumptions, not calibrated against farmer feedback (FORMULAS.md Named Gaps).
"""

import csv
from pathlib import Path

DEFAULT_CURVE_PATH = Path("data/raw/reference/pasture_growth_curve.csv")

# Water-surplus adjustment bounds — FORMULAS.md Group B, not yet calibrated.
WATER_SURPLUS_ADJUSTMENT_MIN = 0.5
WATER_SURPLUS_ADJUSTMENT_MAX = 1.2


def load_growth_curve(path: Path = DEFAULT_CURVE_PATH) -> dict:
    """
    Loads pasture_growth_curve.csv into {(region_id, month): growth_rate_kgdm_ha_day}.
    Skips the '#' comment header block the file starts with.
    Raises FileNotFoundError with a clear message if the CSV isn't where expected —
    fails loud, not silent, per the project's verify-don't-assume discipline.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"pasture_growth_curve.csv not found at {path}. This file must exist before "
            f"estimate_pasture_growth_rate() can look anything up — see "
            f"build_pasture_growth_curve.py to (re)generate it."
        )
    curve = {}
    with open(path, newline="") as f:
        # skip comment lines and the blank line before the real header
        lines = [line for line in f if not line.lstrip().startswith("#")]
    reader = csv.DictReader(l for l in lines if l.strip())
    for row in reader:
        key = (row["region_id"], int(row["month"]))
        curve[key] = float(row["growth_rate_kgdm_ha_day"])
    if not curve:
        raise ValueError(f"pasture_growth_curve.csv at {path} loaded but contained no "
                          f"usable rows — check the file wasn't truncated or malformed.")
    return curve


def seasonal_baseline(region_id: str, month: int, curve: dict) -> float:
    """
    Looks up the region's baseline growth rate (kg DM/ha/day) for a calendar month
    (1-12) from a pre-loaded curve dict (see load_growth_curve()).
    Raises KeyError with a clear message for an unknown region or bad month, rather
    than silently returning 0 or a default — a silent 0 here would look like "no
    growth" instead of "this region/month isn't in the data," which is a materially
    different and dangerous failure mode for a farmer-facing tool.
    """
    if not (1 <= month <= 12):
        raise ValueError(f"month must be 1-12, got {month}")
    key = (region_id, month)
    if key not in curve:
        known_regions = sorted(set(r for r, m in curve.keys()))
        raise KeyError(
            f"No growth curve data for region_id={region_id!r}, month={month}. "
            f"Known regions in the loaded curve: {known_regions}. If this is a new "
            f"region, add it to REGION_SOURCES in build_pasture_growth_curve.py and "
            f"regenerate the CSV — do not guess a value here."
        )
    return curve[key]


def water_surplus_adjustment(water_surplus_today: float,
                              water_surplus_monthly_norm: float) -> float:
    """
    FORMULAS.md Group B: clip(water_surplus_today / water_surplus_monthly_norm, 0.5, 1.2)
    water_surplus = rainfall - ET0 (both already computed upstream, e.g. in the weather
    EDA notebook's feature engineering).
    Raises ValueError on a non-positive norm rather than dividing by zero/negative and
    returning a nonsense ratio.
    """
    if water_surplus_monthly_norm <= 0:
        raise ValueError(
            f"water_surplus_monthly_norm must be > 0, got {water_surplus_monthly_norm}. "
            f"A zero or negative norm makes the ratio meaningless, not just risky."
        )
    ratio = water_surplus_today / water_surplus_monthly_norm
    return max(WATER_SURPLUS_ADJUSTMENT_MIN, min(WATER_SURPLUS_ADJUSTMENT_MAX, ratio))


def estimate_pasture_growth_rate(region_id: str, month: int, water_surplus_today: float,
                                  water_surplus_monthly_norm: float, curve: dict) -> dict:
    """
    growth_rate_kgdm_ha_day = seasonal_baseline(region, month) x water_surplus_adjustment
    Returns {"growth_rate_kgdm_ha_day", "baseline_kgdm_ha_day", "adjustment_factor"} so
    callers/tests can see the baseline and adjustment separately, not just the product —
    matters for debugging when a number looks wrong.
    """
    baseline = seasonal_baseline(region_id, month, curve)
    adjustment = water_surplus_adjustment(water_surplus_today, water_surplus_monthly_norm)
    return {
        "growth_rate_kgdm_ha_day": round(baseline * adjustment, 2),
        "baseline_kgdm_ha_day": baseline,
        "adjustment_factor": round(adjustment, 4),
    }


def effective_hectares(total_hectares: float, non_grazeable_hectares: float = 0.0) -> float:
    """
    FORMULAS.md Group B: effective_hectares = total_hectares - non_grazeable_hectares
    Farmer-confirmed definition. Raises ValueError if non_grazeable exceeds total —
    a farm can't have negative grazeable area.
    """
    if total_hectares <= 0:
        raise ValueError(f"total_hectares must be > 0, got {total_hectares}")
    if non_grazeable_hectares < 0:
        raise ValueError(f"non_grazeable_hectares can't be negative, got "
                          f"{non_grazeable_hectares}")
    result = total_hectares - non_grazeable_hectares
    if result <= 0:
        raise ValueError(
            f"non_grazeable_hectares ({non_grazeable_hectares}) leaves zero or negative "
            f"grazeable area on a {total_hectares}ha farm — check the inputs, this isn't "
            f"a valid farm to model."
        )
    return result


def daily_pasture_grown_kgDM(growth_rate_kgdm_ha_day: float, effective_ha: float) -> float:
    """FORMULAS.md Group B: daily_pasture_grown_kgDM = growth_rate x effective_hectares"""
    return round(growth_rate_kgdm_ha_day * effective_ha, 1)


def net_daily_change_kgDM(daily_pasture_grown: float, daily_feed_demand: float) -> dict:
    """
    Group C2 Signal 1 — FLOW BALANCE (direction + magnitude, no cover needed).
    net_daily_change_kgDM = daily_pasture_grown_kgDM - daily_feed_demand_kgDM
    <0 -> sell pressure (deficit, pasture shrinking) · >0 -> buy/hold capacity (surplus)
    This is the real trend signal FORMULAS.md flags as "NOT YET BUILT" — it replaces the
    stocking_ratio fallback currently used in recommendation_engine.py's
    pasture_signals_from_stocking_ratio(). Swap that function's caller over to this one.
    Returns a dict with a "direction" label so callers don't need to re-derive the sign.
    """
    net = round(daily_pasture_grown - daily_feed_demand, 1)
    if net < 0:
        direction = "deficit"
    elif net > 0:
        direction = "surplus"
    else:
        direction = "balanced"
    return {"net_daily_change_kgDM": net, "direction": direction}


# --- Tests: realistic inputs + deliberate failure cases ---
if __name__ == "__main__":
    # Build a small in-memory curve for testing rather than requiring the real CSV on
    # disk in every environment this module might be imported into for a quick check.
    # (load_growth_curve() itself is tested separately below against the real file.)
    test_curve = {
        ("South_Taranaki_N_Whanganui", 9): 69.8,   # spring peak
        ("South_Taranaki_N_Whanganui", 6): 12.6,   # winter trough
        ("South_Waikato_King_Country", 11): 54.3,
    }

    # Realistic case 1: Taranaki spring, water surplus at norm (adjustment = 1.0)
    r1 = estimate_pasture_growth_rate(
        "South_Taranaki_N_Whanganui", 9, water_surplus_today=20.0,
        water_surplus_monthly_norm=20.0, curve=test_curve,
    )
    print(r1)
    assert r1["growth_rate_kgdm_ha_day"] == 69.8
    assert r1["adjustment_factor"] == 1.0

    # Realistic case 2: Taranaki winter, dry (adjustment clips to the 0.5 floor)
    r2 = estimate_pasture_growth_rate(
        "South_Taranaki_N_Whanganui", 6, water_surplus_today=2.0,
        water_surplus_monthly_norm=20.0, curve=test_curve,
    )
    print(r2)
    assert r2["adjustment_factor"] == 0.5
    assert r2["growth_rate_kgdm_ha_day"] == round(12.6 * 0.5, 2)

    # Realistic case 3: very wet, adjustment clips to the 1.2 ceiling
    r3 = estimate_pasture_growth_rate(
        "South_Waikato_King_Country", 11, water_surplus_today=50.0,
        water_surplus_monthly_norm=20.0, curve=test_curve,
    )
    assert r3["adjustment_factor"] == 1.2

    # Effective hectares + daily pasture grown, chained together
    eff_ha = effective_hectares(total_hectares=120, non_grazeable_hectares=15)
    assert eff_ha == 105
    grown = daily_pasture_grown_kgDM(r1["growth_rate_kgdm_ha_day"], eff_ha)
    print("daily pasture grown:", grown, "kg DM")

    # Group C2 Signal 1 — flow balance, both directions
    deficit = net_daily_change_kgDM(daily_pasture_grown=500, daily_feed_demand=800)
    assert deficit["direction"] == "deficit" and deficit["net_daily_change_kgDM"] == -300
    surplus = net_daily_change_kgDM(daily_pasture_grown=900, daily_feed_demand=800)
    assert surplus["direction"] == "surplus"
    balanced = net_daily_change_kgDM(daily_pasture_grown=800, daily_feed_demand=800)
    assert balanced["direction"] == "balanced"
    print("flow balance cases:", deficit, surplus, balanced)

    # --- Failure cases ---
    # Unknown region/month should raise KeyError, not silently return 0
    try:
        seasonal_baseline("Nonexistent_Region", 5, test_curve)
        raise AssertionError("expected KeyError for unknown region")
    except KeyError:
        pass

    # Bad month should raise ValueError
    try:
        seasonal_baseline("South_Waikato_King_Country", 13, test_curve)
        raise AssertionError("expected ValueError for month=13")
    except ValueError:
        pass

    # Zero/negative water_surplus_monthly_norm should raise, not divide by zero silently
    try:
        water_surplus_adjustment(10.0, 0)
        raise AssertionError("expected ValueError for norm=0")
    except ValueError:
        pass

    # non_grazeable_hectares >= total_hectares should raise
    try:
        effective_hectares(total_hectares=50, non_grazeable_hectares=50)
        raise AssertionError("expected ValueError for fully non-grazeable farm")
    except ValueError:
        pass

    # --- Test load_growth_curve() against the real file, if present ---
    real_path = DEFAULT_CURVE_PATH
    if real_path.exists():
        real_curve = load_growth_curve(real_path)
        assert ("South_Taranaki_N_Whanganui", 9) in real_curve
        print(f"load_growth_curve(): loaded {len(real_curve)} rows from {real_path}, "
              f"real-file check passed.")
    else:
        print(f"NOTE: {real_path} not found in this environment — "
              f"load_growth_curve() exercised structurally only, not against the real "
              f"file. Run this test again once the CSV is in place in the repo.")

    print("All tests passed.")