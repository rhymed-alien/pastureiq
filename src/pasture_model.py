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
from datetime import datetime, date, timedelta
from config import REFERENCE_DIR, WEATHER_DIR

DEFAULT_CURVE_PATH = REFERENCE_DIR / "pasture_growth_curve.csv"

# Water-surplus adjustment bounds — FORMULAS.md Group B, not yet calibrated against
# farmer feedback, but now at least numerically sound (see below).
WATER_SURPLUS_ADJUSTMENT_MIN = 0.5
WATER_SURPLUS_ADJUSTMENT_MAX = 1.2

# --- Scale constants for the difference-based adjustment (redesigned 2026-07-17) ---
# FORMULAS.md originally specified a RATIO: clip(today/norm, 0.5, 1.2). That's broken
# for this variable: water_surplus = rainfall - ET0 is genuinely negative or near-zero
# across NZ summer (confirmed against real data — e.g. Waikato February's monthly norm
# is -0.004 mm/day, several regions go negative Jan-Mar). Dividing by a near-zero or
# sign-crossing denominator produced ratios ranging from -75 to +565 in a real sampling
# across all three regions — not "too wide," actually unstable/meaningless.
#
# Redesigned as a DIFFERENCE instead: today - norm, scaled by real percentile deviations
# so it still reaches the same MIN/MAX bounds at sensible real-world extremes rather than
# an arbitrary ratio threshold. Scale values are the actual 5th/95th percentile deviation
# sampled across all three regions, all three horizon windows, weekly across the full
# weather record (n=5328): 5th percentile -3.75mm (dry), 95th percentile +5.22mm (wet).
# Asymmetric on purpose — matches the original bounds' own asymmetry (0.5 floor, 1.2
# ceiling): drought suppresses growth more than excess rain boosts it.
WATER_SURPLUS_DRY_SCALE_MM = 3.75   # deviation at which MIN (0.5) is reached
WATER_SURPLUS_WET_SCALE_MM = 5.22   # deviation at which MAX (1.2) is reached


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


def load_weather_data(region_id: str, path: Path | None = None) -> list:
    """
    Loads weather_{region_id}.csv into a sorted list of (date, water_surplus_mm) tuples,
    where water_surplus = precipitation_sum - et0_fao_evapotranspiration (both real
    columns in the pulled weather data, per config.WEATHER_VARIABLES).

    Filename convention: WEATHER_DIR / f"weather_{region_id}.csv" — matches the real
    files (weather_waikato.csv, weather_taranaki.csv, weather_auckland.csv) and the
    real config.REGIONS keys (waikato/taranaki/auckland) exactly, confirmed 2026-07-17.
    """
    path = path or (WEATHER_DIR / f"weather_{region_id}.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"Weather data not found at {path} for region_id={region_id!r}. Check the "
            f"region_id matches a real weather_{{region_id}}.csv file, and that it's "
            f"been pulled via src/pull_weather.py."
        )
    surplus = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            d = datetime.strptime(row["time"], "%Y-%m-%d").date()
            ws = float(row["precipitation_sum"]) - float(row["et0_fao_evapotranspiration"])
            surplus.append((d, ws))
    surplus.sort(key=lambda x: x[0])
    if not surplus:
        raise ValueError(f"{path} loaded but contained no usable rows.")
    return surplus


def get_water_surplus_today(region_id: str, target_date: date, weather_data: list) -> float:
    """
    Looks up the exact day's water surplus (rainfall - ET0, mm) for target_date.
    Raises ValueError if that exact date isn't in the data — e.g. asking for a date
    beyond the weather pull's range, or a genuinely missing day — rather than silently
    falling back to some other day and pretending it's "today."
    """
    for d, ws in weather_data:
        if d == target_date:
            return ws
    dates = [d for d, _ in weather_data]
    raise ValueError(
        f"No weather data for {target_date} in region_id={region_id!r}. Data covers "
        f"{min(dates)} to {max(dates)}. If target_date is beyond that range, this needs "
        f"a live forecast pull (get_forecast_weather(), not yet built — see MRS.md "
        f"Section 3.2), not historical data."
    )


def get_trailing_water_surplus(region_id: str, target_date: date, window_days: int,
                                weather_data: list) -> dict:
    """
    Mean water surplus (mm/day) over the `window_days` ending at target_date inclusive.

    THIS IS THE FIX for horizon-invariant scoring: get_water_surplus_today() alone gave
    every horizon (7/14/28 day) the exact same single-day input, so net_daily_change_kgDM
    — and every downstream score — came out identical regardless of horizon. There's no
    live weather forecast yet (get_forecast_weather() isn't built — MRS.md Section 3.2),
    so this can't be a real forward-looking forecast. Instead: window_days = horizon_days,
    so the 7-day horizon uses the last 7 days' actual conditions (responsive, "specific
    daily" character) and the 28-day horizon uses the last 28 days' average (smoothed,
    "trend/outlook" character) — matching Group F's stated design rule that longer
    horizons should read as trend, not a daily forecast, even though this is a trailing
    proxy (assumes recent conditions persist forward) rather than a genuine forecast.

    Raises ValueError if the window extends before the earliest data available, rather
    than silently using a shorter window and calling it something it isn't.

    Returns {"mean_water_surplus_mm", "n_days", "window_start", "window_end"}.
    """
    if window_days <= 0:
        raise ValueError(f"window_days must be > 0, got {window_days}")
    window_start = target_date - timedelta(days=window_days - 1)
    window_values = [ws for d, ws in weather_data if window_start <= d <= target_date]
    if len(window_values) < window_days:
        dates = [d for d, _ in weather_data]
        raise ValueError(
            f"Trailing {window_days}-day window ({window_start} to {target_date}) for "
            f"region_id={region_id!r} only found {len(window_values)} of {window_days} "
            f"expected days — likely extends before the data's start ({min(dates)}). "
            f"Choose a later target_date or a shorter window."
        )
    return {
        "mean_water_surplus_mm": round(sum(window_values) / len(window_values), 3),
        "n_days": len(window_values),
        "window_start": window_start,
        "window_end": target_date,
    }


def get_water_surplus_monthly_norm(region_id: str, month: int, weather_data: list,
                                    exclude_year: int | None = None) -> dict:
    """
    Historical mean daily water surplus (mm) for calendar month `month`, across all
    years present in weather_data. Same backtest-hygiene pattern as
    market_model.get_seasonal_average(): pass exclude_year (target_date.year) when
    evaluating a real historical date, so the norm doesn't include the very day being
    compared against itself.

    Returns {"mean_water_surplus_mm", "n_days", "years_used"} — n_days matters for the
    same reason market_model.py's n_years does: a norm built from a handful of days is
    weaker than one built from a full multi-year record.
    """
    if not (1 <= month <= 12):
        raise ValueError(f"month must be 1-12, got {month}")
    matches = [(d, ws) for d, ws in weather_data
               if d.month == month and d.year != exclude_year]
    if not matches:
        raise ValueError(
            f"No historical water-surplus data for region_id={region_id!r}, month="
            f"{month} (excluding year={exclude_year}) — cannot compute a norm from "
            f"zero data points."
        )
    values = [ws for _, ws in matches]
    return {
        "mean_water_surplus_mm": round(sum(values) / len(values), 3),
        "n_days": len(matches),
        "years_used": sorted(set(d.year for d, _ in matches)),
    }


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
    REDESIGNED 2026-07-17 — see the WATER_SURPLUS_DRY_SCALE_MM/WET_SCALE_MM comment
    above for the full story. Original FORMULAS.md formula was a ratio
    (today/norm), which is numerically broken for this variable: the previous version
    of this function actually raised ValueError whenever water_surplus_monthly_norm was
    <= 0 — confirmed against real data to happen ~4-5 months of the year in every one
    of the three target regions (NZ summer: rainfall regularly falls below ET0). That
    meant the whole pipeline couldn't run in summer, not just "produced an odd number."

    Now a DIFFERENCE from norm, scaled asymmetrically to real percentile deviations so
    it reaches the same MIN/MAX bounds at genuinely extreme wet/dry conditions:
        adjustment = clip(1 + deviation/scale * (bound - 1), MIN, MAX)
    where deviation = today - norm, and scale/bound depend on sign (dry vs wet).
    Numerically stable for any norm value, including negative or zero.
    """
    deviation = water_surplus_today - water_surplus_monthly_norm
    if deviation >= 0:
        adjustment = 1.0 + (deviation / WATER_SURPLUS_WET_SCALE_MM) * (WATER_SURPLUS_ADJUSTMENT_MAX - 1.0)
    else:
        adjustment = 1.0 + (deviation / WATER_SURPLUS_DRY_SCALE_MM) * (1.0 - WATER_SURPLUS_ADJUSTMENT_MIN)
    return max(WATER_SURPLUS_ADJUSTMENT_MIN, min(WATER_SURPLUS_ADJUSTMENT_MAX, adjustment))


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
        ("taranaki", 9): 69.8,   # spring peak
        ("taranaki", 6): 12.6,   # winter trough
        ("waikato", 11): 54.3,
    }

    # Realistic case 1: Taranaki spring, water surplus at norm (adjustment = 1.0)
    r1 = estimate_pasture_growth_rate(
        "taranaki", 9, water_surplus_today=20.0,
        water_surplus_monthly_norm=20.0, curve=test_curve,
    )
    print(r1)
    assert r1["growth_rate_kgdm_ha_day"] == 69.8
    assert r1["adjustment_factor"] == 1.0

    # Realistic case 2: Taranaki winter, dry (adjustment clips to the 0.5 floor)
    r2 = estimate_pasture_growth_rate(
        "taranaki", 6, water_surplus_today=2.0,
        water_surplus_monthly_norm=20.0, curve=test_curve,
    )
    print(r2)
    assert r2["adjustment_factor"] == 0.5
    assert r2["growth_rate_kgdm_ha_day"] == round(12.6 * 0.5, 2)

    # Realistic case 3: very wet, adjustment clips to the 1.2 ceiling
    r3 = estimate_pasture_growth_rate(
        "waikato", 11, water_surplus_today=50.0,
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
        seasonal_baseline("waikato", 13, test_curve)
        raise AssertionError("expected ValueError for month=13")
    except ValueError:
        pass

    # --- Real-world case that broke the OLD ratio formula: a zero or negative monthly
    # norm. Confirmed against real data this happens ~4-5 months/year in every region
    # (NZ summer). The old ratio-based version raised ValueError here, which meant the
    # whole pipeline couldn't run in summer at all. The redesigned difference-based
    # version must handle this cleanly, not crash.
    adj_negative_norm = water_surplus_adjustment(water_surplus_today=1.0,
                                                  water_surplus_monthly_norm=-0.5)
    print(f"water_surplus_adjustment with a NEGATIVE norm (real summer case): "
          f"{adj_negative_norm} — must not raise")
    assert WATER_SURPLUS_ADJUSTMENT_MIN <= adj_negative_norm <= WATER_SURPLUS_ADJUSTMENT_MAX

    adj_zero_norm = water_surplus_adjustment(water_surplus_today=2.0,
                                              water_surplus_monthly_norm=0.0)
    print(f"water_surplus_adjustment with a ZERO norm: {adj_zero_norm} — must not raise")
    assert WATER_SURPLUS_ADJUSTMENT_MIN <= adj_zero_norm <= WATER_SURPLUS_ADJUSTMENT_MAX

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
        assert ("taranaki", 9) in real_curve
        print(f"load_growth_curve(): loaded {len(real_curve)} rows from {real_path}, "
              f"real-file check passed.")
    else:
        print(f"NOTE: {real_path} not found in this environment — "
              f"load_growth_curve() exercised structurally only, not against the real "
              f"file. Run this test again once the CSV is in place in the repo.")

    # --- Test water surplus functions against real weather data, if present ---
    real_weather_path = WEATHER_DIR / "weather_taranaki.csv"
    if real_weather_path.exists():
        weather = load_weather_data("taranaki", real_weather_path)
        # A specific real day, checked by hand against the raw CSV: 2025-09-15,
        # rain 1.2mm, ET0 1.89mm -> water surplus -0.69mm
        ws_today = get_water_surplus_today("taranaki", date(2025, 9, 15), weather)
        assert abs(ws_today - (-0.69)) < 0.01, f"expected -0.69, got {ws_today}"

        norm = get_water_surplus_monthly_norm("taranaki", 9, weather, exclude_year=2025)
        print(f"get_water_surplus_monthly_norm(taranaki, Sept, 2025 excluded): {norm}")
        assert norm["n_days"] > 250  # ~30 days/year x 9 remaining years

        # Failure case: a date beyond the weather pull's range should raise, not
        # silently return something from a different date
        try:
            get_water_surplus_today("taranaki", date(2099, 1, 1), weather)
            raise AssertionError("expected ValueError for a date beyond the data range")
        except ValueError:
            pass

        # --- Trailing window tests — the actual horizon-invariance fix ---
        w7 = get_trailing_water_surplus("taranaki", date(2025, 9, 15), 7, weather)
        w14 = get_trailing_water_surplus("taranaki", date(2025, 9, 15), 14, weather)
        w28 = get_trailing_water_surplus("taranaki", date(2025, 9, 15), 28, weather)
        print(f"Trailing windows for 2025-09-15: 7d={w7['mean_water_surplus_mm']}, "
              f"14d={w14['mean_water_surplus_mm']}, 28d={w28['mean_water_surplus_mm']}")
        assert w7["n_days"] == 7 and w14["n_days"] == 14 and w28["n_days"] == 28
        # The three windows should generally differ — proves horizons now actually see
        # different inputs, not the same single day repeated three times
        assert not (w7["mean_water_surplus_mm"] == w14["mean_water_surplus_mm"] ==
                    w28["mean_water_surplus_mm"]), (
            "trailing windows came out identical — horizon-invariance may not actually "
            "be fixed, check the underlying daily data isn't unrealistically constant"
        )

        # Failure case: window extending before the data's start should raise
        try:
            get_trailing_water_surplus("taranaki", date(2015, 1, 5), 28, weather)
            raise AssertionError("expected ValueError for a window before data start")
        except ValueError:
            pass

        print("Trailing water surplus: real-file checks passed.")
        print("Water surplus functions: real-file checks passed.")
    else:
        print(f"NOTE: {real_weather_path} not found in this environment — water "
              f"surplus functions exercised structurally only.")

    print("All tests passed.")