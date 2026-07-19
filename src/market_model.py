"""
market_model.py — Group D: MARKET SIGNAL (price_vs_seasonal only — no Prophet forecast
yet, that's MP3, see FORMULAS.md Group D).

Data source: data/raw/market/blnz_farmgate_prices.csv, real columns confirmed 2026-07-17:
    date, farm_year, series, price, unit
7 series, each a single consistent unit — no within-series unit mixing to handle:
    all_grades_lamb ($/hd), all_grades_mutton ($/hd), mx1_mutton ($/hd),
    ym_lamb ($/hd), m_bull_270_295kg (c/kg), m_cow_170_195kg (c/kg),
    p_steer_heifer_270_295kg (c/kg)

⚠ OPEN DECISION, NOT RESOLVED HERE: this module works on `series` (the CSV's real
market-class names) directly. It does NOT map stock_units.py's feed-side classes
(e.g. "ewe", "hoggets") to price series (e.g. "ym_lamb", "all_grades_mutton") — a
farmer's ewe mob sells as mutton, not "ewe," and that mapping isn't specified anywhere
in FORMULAS.md. Building it into this module would mean guessing a mapping FORMULAS.md
never made. Whoever calls this module (run_recommendations.py) needs to supply the
right `series` name for a given stock_class — flagged as a TODO there, not solved here.
"""

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from config import MARKET_DIR

DEFAULT_PRICE_PATH = MARKET_DIR / "blnz_farmgate_prices.csv"


def load_price_data(path: Path = DEFAULT_PRICE_PATH) -> dict:
    """
    Loads blnz_farmgate_prices.csv into {series: [(date, price), ...]}, sorted by date.
    Raises FileNotFoundError with a clear message if missing — fails loud, not silent.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"blnz_farmgate_prices.csv not found at {path}. This file must exist before "
            f"price_vs_seasonal() can look anything up."
        )
    data = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            d = datetime.strptime(row["date"], "%Y-%m-%d").date()
            data[row["series"]].append((d, float(row["price"])))
    for series in data:
        data[series].sort(key=lambda x: x[0])
    if not data:
        raise ValueError(f"{path} loaded but contained no usable rows.")
    return dict(data)


def get_seasonal_average(series: str, month: int, price_data: dict,
                          exclude_year: int | None = None) -> dict:
    """
    Mean price for `series` in calendar month `month`, across all years in price_data.

    exclude_year: if evaluating a specific historical data point (e.g. backtesting
    price_vs_seasonal for a real past date), pass that date's year here so the average
    doesn't include the very point being compared against itself — that would silently
    understate the deviation. Leave None for a genuinely forward-looking "current"
    evaluation, where the current year's data for this month doesn't exist yet anyway.

    Returns {"mean_price", "n_years", "years_used"} — n_years matters: a 2-year average
    is a much weaker seasonal baseline than a 9-year one, and callers/output should be
    able to reflect that rather than treating every seasonal average as equally solid.
    """
    if series not in price_data:
        raise KeyError(f"'{series}' not in price_data. Known series: "
                        f"{sorted(price_data.keys())}")
    if not (1 <= month <= 12):
        raise ValueError(f"month must be 1-12, got {month}")

    matches = [(d, p) for d, p in price_data[series]
               if d.month == month and d.year != exclude_year]
    if not matches:
        raise ValueError(
            f"No historical data for series={series!r}, month={month} "
            f"(excluding year={exclude_year}) — cannot compute a seasonal average from "
            f"zero data points."
        )
    prices = [p for _, p in matches]
    return {
        "mean_price": round(sum(prices) / len(prices), 2),
        "n_years": len(matches),
        "years_used": sorted(set(d.year for d, _ in matches)),
    }


def get_price_for_month(series: str, year: int, month: int, price_data: dict) -> float:
    """
    Looks up the exact monthly price for `series` in a given year/month. Price data is
    one row per calendar month (see DATA_SOURCES.md), so this is a direct lookup, not
    an average. Raises KeyError if that exact year/month isn't in the data — e.g. a
    target_date beyond the price pull's range — rather than silently substituting a
    nearby month.
    """
    if series not in price_data:
        raise KeyError(f"'{series}' not in price_data. Known series: "
                        f"{sorted(price_data.keys())}")
    for d, p in price_data[series]:
        if d.year == year and d.month == month:
            return p
    dates = [d for d, _ in price_data[series]]
    raise KeyError(
        f"No price for series={series!r}, {year}-{month:02d}. Data covers "
        f"{min(dates)} to {max(dates)}."
    )


def price_vs_seasonal(series: str, current_price: float, month: int, price_data: dict,
                       exclude_year: int | None = None) -> dict:
    """
    FORMULAS.md Group D:
        price_vs_seasonal = (current_price - seasonal_avg_price) / seasonal_avg_price
    >0 -> price is above seasonal average (favourable to sell)
    <0 -> price is below seasonal average (favourable to buy)
    Returns the seasonal average's n_years alongside the ratio, so a caller can see
    whether "above seasonal average" rests on 2 years of data or 9.
    """
    seasonal = get_seasonal_average(series, month, price_data, exclude_year)
    ratio = (current_price - seasonal["mean_price"]) / seasonal["mean_price"]
    return {
        "price_vs_seasonal_pct": round(ratio, 4),
        "current_price": current_price,
        "seasonal_avg_price": seasonal["mean_price"],
        "seasonal_avg_n_years": seasonal["n_years"],
    }


def classify_price_signal(price_vs_seasonal_pct: float, favourable_threshold: float = 0.05,
                           low_threshold: float = -0.05) -> str:
    """
    Simple descriptive bucket, NOT a scoring function — Group E (recommendation_engine.py)
    already owns scoring. This just labels the signal for display/notes:
        "favourable_to_sell" | "favourable_to_buy" | "neutral"
    Thresholds are placeholders (Open Decision, same status as recommendation_engine.py's
    own placeholder caps) — not calibrated against real farmer decisions yet.
    """
    if price_vs_seasonal_pct >= favourable_threshold:
        return "favourable_to_sell"
    if price_vs_seasonal_pct <= low_threshold:
        return "favourable_to_buy"
    return "neutral"


# --- Tests: realistic inputs + deliberate failure cases, against the REAL CSV ---
if __name__ == "__main__":
    price_data = load_price_data()
    print("Series loaded:", sorted(price_data.keys()))

    # Realistic case 1: ym_lamb in September (spring/early-summer peak per the data)
    sept_avg = get_seasonal_average("ym_lamb", 9, price_data)
    print("ym_lamb September seasonal avg:", sept_avg)
    assert sept_avg["n_years"] >= 8  # 2016-2025 Septembers present

    # Realistic case 2: price_vs_seasonal for a real historical point, September 2025,
    # excluding 2025 from its own average (proper backtest hygiene). Price looked up
    # via get_price_for_month() now, not hand-copied from the CSV.
    sept_2025_price = get_price_for_month("ym_lamb", 2025, 9, price_data)
    assert sept_2025_price == 165.66  # confirms the lookup matches the known real value
    pvs = price_vs_seasonal("ym_lamb", sept_2025_price, 9, price_data, exclude_year=2025)
    print("Sept 2025 ym_lamb vs seasonal (2025 excluded):", pvs)
    assert pvs["seasonal_avg_n_years"] == sept_avg["n_years"] - 1  # one year removed

    # Failure case: a month beyond the data's range should raise, not substitute
    try:
        get_price_for_month("ym_lamb", 2099, 1, price_data)
        raise AssertionError("expected KeyError for a date beyond the data range")
    except KeyError:
        pass

    # Realistic case 3: classify the signal
    label = classify_price_signal(pvs["price_vs_seasonal_pct"])
    print("Signal:", label)

    # Realistic case 4: a c/kg series works identically (unit-agnostic on purpose —
    # this module compares like-for-like within a series, never across series/units)
    steer_avg = get_seasonal_average("p_steer_heifer_270_295kg", 9, price_data)
    print("p_steer_heifer_270_295kg September seasonal avg:", steer_avg)

    # --- Failure cases ---
    try:
        get_seasonal_average("nonexistent_series", 9, price_data)
        raise AssertionError("expected KeyError")
    except KeyError:
        pass

    try:
        get_seasonal_average("ym_lamb", 13, price_data)
        raise AssertionError("expected ValueError for month=13")
    except ValueError:
        pass

    # A month/exclude_year combo with zero remaining data points should raise, not
    # silently return a nonsense average
    try:
        # ym_lamb has data 2016-2026; excluding every one of those years for a given
        # month one at a time works fine, but excluding a year that's the ONLY year
        # present for a month should raise. October only has 2016-2025 (10 years) so
        # this constructed case uses a narrower series check instead:
        thin_data = {"test_series": [(datetime(2020, 5, 1).date(), 100.0)]}
        get_seasonal_average("test_series", 5, thin_data, exclude_year=2020)
        raise AssertionError("expected ValueError for zero remaining data points")
    except ValueError:
        pass

    print("All tests passed.")