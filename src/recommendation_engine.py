"""
recommendation_engine.py — Group E: BUY/SELL RECOMMENDATION (crude stub)

Purpose: wire an end-to-end path from signals -> ranked action, even before
Group B (pasture growth) and Group D (market price forecast) are fully built.
This is deliberately crude — hand-set weights, no tuning, no bias correction
applied yet. It exists so there is an OUTPUT to test and show, per
FORMULAS.md Group E: "Combines C and D. A scoring + ranking system."

⚠ STATUS: [MP2 logic, placeholder]. Weights (W1, W2) are hand-set guesses,
NOT tuned against the predictions log (Group G) yet — see FORMULAS.md Open
Decision on Group E score->action thresholds.

Inputs this module expects (from upstream, some of which don't exist yet):
- pasture_deficit_signal / pasture_surplus_signal: from Group C2 Signal 1
  (flow balance, not built) or Signal 2 (stocking_ratio, built). Until flow
  balance exists, this stub derives both from stocking_ratio as a fallback —
  flagged explicitly below, swap out when Group C Signal 1 lands.
- price_favourable_signal / price_low_signal: from Group D (price_vs_seasonal,
  not built). Until that exists, pass price_vs_seasonal_pct manually or
  omit — the stub degrades gracefully to pasture-only scoring, flagged in
  output via `price_data_available`.
- class_transition_penalty: quantifies the lamb->hogget price drop. Hard-set
  placeholder below — FORMULAS.md Group E Open Decision #1, still TBD for
  real figure.

Does NOT apply Group G bias correction (not built for live predictions yet).
Does NOT use minimum_residual_cover (not needed for the cover-free path).
"""

from dataclasses import dataclass, field


# --- Hand-set weights (placeholder — TBD tune against predictions log) ---
W1_PASTURE = 0.6
W2_PRICE = 0.4

# --- Placeholder class-transition penalty (Open Decision #1, unresolved) ---
# Flat guess: crossing the lamb->hogget boundary costs ~15% of score.
# Swap for a real cents/kg figure once quantified.
LAMB_HOGGET_TRANSITION_PENALTY = 0.15

# --- Score -> action thresholds (Open Decision #2, unresolved) ---
# Placeholder cut-offs. Anything in between is HOLD.
SELL_THRESHOLD = 0.35
BUY_THRESHOLD = 0.35


def normalize_signal(value: float, cap: float) -> float:
    """
    Clip a raw signal to 0-1 by dividing by a cap and bounding.
    Placeholder normalization — no real distribution analysis behind `cap`
    yet. Negative values clip to 0 (a signal can't be "negatively deficit").
    """
    if cap <= 0:
        raise ValueError(f"cap must be > 0, got {cap}")
    return max(0.0, min(1.0, value / cap))


def pasture_signals_from_stocking_ratio(stocking_ratio: float) -> dict:
    """
    FALLBACK ONLY. Derives deficit/surplus signals from Group C2 Signal 2
    (stocking_ratio) because Group C2 Signal 1 (flow balance) isn't built.
    stocking_ratio > 1 -> overstocked -> deficit pressure.
    stocking_ratio < 1 -> understocked -> surplus/room to buy.

    ⚠ Replace this function's caller with real flow-balance signals the
    moment net_daily_change_kgDM (Group C) exists — stocking_ratio is a
    structural snapshot, not a trend, and will produce false urgency on
    farms that are stably overstocked but not currently tightening.
    """
    deficit_raw = max(0.0, stocking_ratio - 1.0)
    surplus_raw = max(0.0, 1.0 - stocking_ratio)
    return {
        "pasture_deficit_signal": normalize_signal(deficit_raw, cap=1.0),
        "pasture_surplus_signal": normalize_signal(surplus_raw, cap=1.0),
        "source": "stocking_ratio_fallback",  # not flow balance
    }


def score_sell(
    pasture_deficit_signal: float,
    price_favourable_signal: float | None,
    crosses_lamb_hogget_boundary: bool = False,
) -> dict:
    """
    sell_score = W1 * pasture_deficit_signal + W2 * price_favourable_signal
                 - class_transition_penalty

    If price_favourable_signal is None (Group D not wired yet), scores on
    pasture alone and flags price_data_available = False so the ranking
    step / plain-English output can be honest about what's missing.
    """
    price_available = price_favourable_signal is not None
    price_component = (price_favourable_signal or 0.0) * W2_PRICE
    pasture_component = pasture_deficit_signal * W1_PASTURE

    penalty = LAMB_HOGGET_TRANSITION_PENALTY if crosses_lamb_hogget_boundary else 0.0

    raw_score = pasture_component + (price_component if price_available else 0.0) - penalty

    # If price data is missing, rescale so pasture-only score can still
    # cross thresholds — otherwise it's structurally capped at W1_PASTURE.
    if not price_available:
        raw_score = pasture_component / W1_PASTURE * (W1_PASTURE + W2_PRICE) - penalty

    return {
        "score": round(raw_score, 4),
        "price_data_available": price_available,
        "penalty_applied": penalty,
    }


def score_buy(
    pasture_surplus_signal: float,
    price_low_signal: float | None,
) -> dict:
    """buy_score = W1 * pasture_surplus_signal + W2 * price_low_signal"""
    price_available = price_low_signal is not None
    pasture_component = pasture_surplus_signal * W1_PASTURE
    price_component = (price_low_signal or 0.0) * W2_PRICE

    raw_score = pasture_component + (price_component if price_available else 0.0)
    if not price_available:
        raw_score = pasture_component / W1_PASTURE * (W1_PASTURE + W2_PRICE)

    return {
        "score": round(raw_score, 4),
        "price_data_available": price_available,
    }


@dataclass
class ActionCandidate:
    stock_class: str
    horizon_days: int
    action: str          # "SELL" | "BUY" | "HOLD"
    score: float
    confidence: str       # from Group F, e.g. "HIGH" / "MEDIUM" / "LOW"
    price_data_available: bool = True
    notes: list = field(default_factory=list)


def classify_action(sell_score: float, buy_score: float) -> str:
    """Placeholder thresholds — FORMULAS.md Group E Open Decision #2."""
    if sell_score >= SELL_THRESHOLD and sell_score >= buy_score:
        return "SELL"
    if buy_score >= BUY_THRESHOLD and buy_score > sell_score:
        return "BUY"
    return "HOLD"


def rank_candidates(candidates: list[ActionCandidate], top_n: int = 2) -> list[ActionCandidate]:
    """
    E3: rank all (class, horizon, action) candidates by score magnitude,
    surface top N. HOLD candidates excluded from ranking — nothing useful
    to rank about a hold, per PROJECT_SPEC output spec (1-2 clear actions).
    Ties broken by shorter horizon (more actionable sooner, higher confidence).
    """
    actionable = [c for c in candidates if c.action != "HOLD"]
    actionable.sort(key=lambda c: (-c.score, c.horizon_days))
    return actionable[:top_n]


def run_recommendation(
    stock_class: str,
    horizon_days: int,
    stocking_ratio: float,
    confidence: str,
    price_vs_seasonal_pct: float | None = None,
    crosses_lamb_hogget_boundary: bool = False,
) -> ActionCandidate:
    """
    Wires one (class, horizon) pair end-to-end. This is the thin vertical
    slice: stocking_ratio -> pasture signals -> sell/buy scores -> action.
    Loop this over farm_mob x [7, 14, 28] per FORMULAS.md E2 structure.
    """
    pasture = pasture_signals_from_stocking_ratio(stocking_ratio)

    price_favourable = None
    price_low = None
    if price_vs_seasonal_pct is not None:
        # price above seasonal avg = favourable to sell; below = favourable to buy.
        # Placeholder cap of 20% swing -> normalized 0-1. Cap TBD, no real
        # distribution analysis behind it yet (Group D not built).
        price_favourable = normalize_signal(max(0.0, price_vs_seasonal_pct), cap=0.20)
        price_low = normalize_signal(max(0.0, -price_vs_seasonal_pct), cap=0.20)

    sell = score_sell(
        pasture["pasture_deficit_signal"],
        price_favourable,
        crosses_lamb_hogget_boundary,
    )
    buy = score_buy(pasture["pasture_surplus_signal"], price_low)

    action = classify_action(sell["score"], buy["score"])
    final_score = sell["score"] if action == "SELL" else buy["score"] if action == "BUY" else 0.0

    notes = []
    if not sell["price_data_available"]:
        notes.append("price data unavailable — scored on pasture signal only")
    if pasture["source"] == "stocking_ratio_fallback":
        notes.append("pasture signal is a structural snapshot (stocking_ratio), not a trend (flow balance not yet built)")

    return ActionCandidate(
        stock_class=stock_class,
        horizon_days=horizon_days,
        action=action,
        score=final_score,
        confidence=confidence,
        price_data_available=sell["price_data_available"],
        notes=notes,
    )


# --- Tests: realistic inputs + deliberate failure cases ---
if __name__ == "__main__":
    # Realistic case 1: overstocked hard hill farm, no price data yet
    c1 = run_recommendation(
        stock_class="ewes",
        horizon_days=14,
        stocking_ratio=1.4,
        confidence="MEDIUM",
    )
    print(c1)
    assert c1.action == "SELL"
    assert c1.price_data_available is False

    # Realistic case 2: understocked farm, price low vs seasonal -> BUY candidate
    c2 = run_recommendation(
        stock_class="hoggets",
        horizon_days=28,
        stocking_ratio=0.7,
        confidence="LOW",
        price_vs_seasonal_pct=-0.12,
    )
    print(c2)
    assert c2.action == "BUY"

    # Realistic case 3: lamb crossing hogget boundary during a sell window
    c3 = run_recommendation(
        stock_class="lambs",
        horizon_days=7,
        stocking_ratio=1.6,
        confidence="HIGH",
        price_vs_seasonal_pct=0.10,
        crosses_lamb_hogget_boundary=True,
    )
    print(c3)
    assert c3.action == "SELL"
    assert any("stocking_ratio" in n for n in c3.notes)

    # Failure case 1: stocking_ratio at exactly 1.0 -> both signals 0 -> HOLD
    c4 = run_recommendation(stock_class="cows", horizon_days=14, stocking_ratio=1.0, confidence="MEDIUM")
    assert c4.action == "HOLD"

    # Failure case 2: bad cap should raise, not silently misnormalize
    try:
        normalize_signal(0.5, cap=0)
        raise AssertionError("expected ValueError on cap=0")
    except ValueError:
        pass

    # Ranking test: candidates including a HOLD should exclude it from ranking
    ranked = rank_candidates([c1, c2, c3, c4], top_n=2)
    assert c4 not in ranked
    assert len(ranked) == 2
    print("Top actions:", [(c.stock_class, c.horizon_days, c.action, c.score) for c in ranked])

    print("All tests passed.")