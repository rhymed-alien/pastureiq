"""
run_recommendations.py — wires Group A + Group B/C2 + Group E together for one farm.

This is the missing link between "the modules exist" and "the modules talk to each
other." Loops per FORMULAS.md Group E2: for horizon in [7,14,28] x for stock_class in
farm_mob -> score -> rank top 1-2.

Verified 2026-07-17 against the real src/stock_units.py: calculate_total_lsu() and
daily_feed_demand_kgDM() signatures matched what this script already assumed, no
changes needed. stocking_ratio() also exists there and is now wired in below —
previously stubbed to None pending confirmation of where that lookup lived.
"""

from datetime import date
from config import CONFIDENCE_BY_HORIZON, STOCK_CLASS_TO_PRICE_SERIES
from src.stock_units import calculate_total_lsu, daily_feed_demand_kgDM, stocking_ratio as compute_stocking_ratio
from src.pasture_model import (
    load_growth_curve,
    load_weather_data,
    get_trailing_water_surplus,
    get_water_surplus_monthly_norm,
    estimate_pasture_growth_rate,
    effective_hectares,
    daily_pasture_grown_kgDM,
    net_daily_change_kgDM,
)
from src.market_model import load_price_data, get_price_for_month, price_vs_seasonal
from src.recommendation_engine import run_recommendation, rank_candidates


def get_real_price_signal(stock_class: str, target_date: date, price_data: dict) -> float | None:
    """
    Resolves a real price_vs_seasonal_pct for a stock class via
    STOCK_CLASS_TO_PRICE_SERIES (config.py), computed against the real
    blnz_farmgate_prices.csv. Returns None (not an error) for:
      - a stock_class not in the mapping (e.g. the dairy-origin grazing classes,
        deliberately left unmapped — see config.py's comment on the mapping)
      - a stock_class mapped to a series, but with no price data for target_date's
        year/month (e.g. a future date beyond the price pull's range)
    Both cases degrade gracefully through run_recommendation()'s existing
    price_vs_seasonal_pct=None path — same honest "price data unavailable,
    confidence downgraded" behaviour as before, now reached via a real lookup
    attempt rather than an unconditionally-missing manual input.
    """
    series = STOCK_CLASS_TO_PRICE_SERIES.get(stock_class)
    if series is None:
        return None
    try:
        current_price = get_price_for_month(series, target_date.year, target_date.month, price_data)
    except KeyError:
        return None
    pvs = price_vs_seasonal(series, current_price, target_date.month, price_data,
                             exclude_year=target_date.year)
    return pvs["price_vs_seasonal_pct"]


def get_recommendations_for_farm(
    region_id: str,
    target_date: date,          # replaces separate month + hardcoded water surplus values —
                                 # month and today's real water surplus are both derived
                                 # from this against the real weather_{region_id}.csv
    total_hectares: float,
    non_grazeable_hectares: float,
    farm_mob: dict,             # e.g. {"ewe": 400, "hogget": 150}
    terrain_type: str,          # e.g. "hard_hill" — for stocking_ratio's carrying capacity
    price_vs_seasonal_by_class: dict | None = None,  # manual OVERRIDE only now — real
                                 # prices are resolved automatically via
                                 # STOCK_CLASS_TO_PRICE_SERIES + blnz_farmgate_prices.csv.
                                 # A class present here skips the automatic lookup.
    confidence_by_horizon: dict | None = None,        # from Group F, e.g. config.py's dict
):
    """
    Runs Group A -> B/C2 -> D -> E for one farm snapshot, once per stock class in
    farm_mob. Returns the ranked top 1-2 actions across all classes, per
    PROJECT_SPEC's output spec.
    """
    confidence_by_horizon = confidence_by_horizon or CONFIDENCE_BY_HORIZON
    month = target_date.month

    # --- Group A: feed demand (whole farm, all classes combined) — same for every
    # horizon, computed once ---
    total_lsu = calculate_total_lsu(farm_mob)
    feed_demand = daily_feed_demand_kgDM(total_lsu)
    eff_ha = effective_hectares(total_hectares, non_grazeable_hectares)

    # --- Group C2 Signal 2: stocking_ratio (structural context) — also horizon-
    # independent, computed once. Wired to the real stock_units.stocking_ratio(),
    # which raises ValueError if terrain_type isn't fully sourced yet — caught here
    # so one unresolved terrain type doesn't crash the whole recommendation.
    try:
        ratio = compute_stocking_ratio(total_lsu, eff_ha, terrain_type)
    except ValueError as e:
        print(f"NOTE: stocking_ratio unavailable for terrain_type={terrain_type!r}: {e}")
        ratio = None

    curve = load_growth_curve()
    weather = load_weather_data(region_id)
    norm = get_water_surplus_monthly_norm(region_id, month, weather,
                                           exclude_year=target_date.year)

    # --- Group D: real price signals, resolved once per stock class (price doesn't
    # vary by horizon in this data — monthly resolution). Manual override in
    # price_vs_seasonal_by_class takes precedence per class if supplied.
    price_data = load_price_data()
    price_vs_seasonal_by_class = price_vs_seasonal_by_class or {}
    resolved_prices = {}
    for stock_class in farm_mob:
        if stock_class in price_vs_seasonal_by_class:
            resolved_prices[stock_class] = price_vs_seasonal_by_class[stock_class]
        else:
            resolved_prices[stock_class] = get_real_price_signal(stock_class, target_date, price_data)

    # --- Group B/C2 Signal 1 + Group E: recomputed PER HORIZON. This is the fix for
    # horizon-invariant scoring — previously water_surplus_today was a single point-in-
    # time value shared by every horizon, so 7/14/28-day candidates all scored
    # identically. Now each horizon uses a trailing window matching its own length
    # (get_trailing_water_surplus), so a 7-day recommendation responds to the last
    # week's actual conditions while a 28-day one reflects a smoothed longer trend —
    # matching Group F's design rule that longer horizons should read as trend, not a
    # repeated daily snapshot.
    candidates = []
    for horizon_days in (7, 14, 28):
        window = get_trailing_water_surplus(region_id, target_date, horizon_days, weather)
        growth = estimate_pasture_growth_rate(
            region_id, month, window["mean_water_surplus_mm"],
            norm["mean_water_surplus_mm"], curve
        )
        grown = daily_pasture_grown_kgDM(growth["growth_rate_kgdm_ha_day"], eff_ha)
        flow = net_daily_change_kgDM(grown, feed_demand)

        for stock_class in farm_mob:
            candidate = run_recommendation(
                stock_class=stock_class,
                horizon_days=horizon_days,
                region_id=region_id,
                net_daily_change_kgDM=flow["net_daily_change_kgDM"],
                effective_hectares=eff_ha,
                confidence=confidence_by_horizon[horizon_days],
                stocking_ratio=ratio,
                price_vs_seasonal_pct=resolved_prices[stock_class],
                # crosses_lamb_hogget_boundary: TODO, needs lamb age input (optional
                # profile field per PROJECT_SPEC) — omitted here, defaults to False
            )
            candidates.append(candidate)

    return rank_candidates(candidates, top_n=2)


if __name__ == "__main__":
    # Example call with a real date, real weather-derived water surplus, AND real
    # price data now (via STOCK_CLASS_TO_PRICE_SERIES) — the only made-up inputs left
    # are the farm profile itself (hectares, mob, terrain), which would come from the
    # farmer's saved profile in the real app.
    top_actions = get_recommendations_for_farm(
        region_id="taranaki",  # real config.py key
        target_date=date(2025, 9, 15),  # real date within the weather pull's range —
                                          # water surplus computed from real rain/ET0
        total_hectares=120,
        non_grazeable_hectares=15,
        farm_mob={"ewe": 400, "hogget": 150},  # singular "hogget" — confirmed against
                                                 # the real lsu_conversion_table.csv
        terrain_type="steep_hill",  # matches config.REGIONS["taranaki"]["terrain"]
        # price_vs_seasonal_by_class no longer needed here — real prices resolved
        # automatically for "ewe" (-> all_grades_mutton) and "hogget" (-> same).
    )
    for action in top_actions:
        print(action)