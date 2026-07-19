"""
recommendation_engine.py — Group E: BUY/SELL RECOMMENDATION (crude stub)

Purpose: wire an end-to-end path from signals -> ranked action, even before all of
Group D (market price forecast) is fully built. This is deliberately crude — hand-set
weights, no tuning, no bias correction applied yet. It exists so there is an OUTPUT to
test and show, per FORMULAS.md Group E: "Combines C and D. A scoring + ranking system."

⚠ STATUS: [MP2 logic, placeholder]. Weights (W1, W2) are hand-set guesses,
NOT tuned against the predictions log (Group G) yet — see FORMULAS.md Open
Decision on Group E score->action thresholds.

UPDATED 2026-07-17: pasture scoring now runs on Group C2 Signal 1 (flow balance,
net_daily_change_kgDM from pasture_model.py) instead of the stocking_ratio fallback.
Flow balance is a real trend signal (is pasture currently tightening or not); it
replaces stocking_ratio as the thing that drives sell/buy SCORING.

stocking_ratio (Group C2 Signal 2) is NOT dropped — it's genuinely complementary, not
redundant: flow balance answers "is pasture tightening right now," stocking_ratio
answers "is this farm structurally over/understocked for its land class." A farm can
be stably overstocked (high stocking_ratio) while flow balance is neutral (not
currently tightening), or vice versa. Both are surfaced: flow balance drives the
score, stocking_ratio is carried as structural context in `notes` so the two can be
read together rather than one silently overriding the other.

Inputs this module expects:
- net_daily_change_kgDM, effective_hectares: from Group C2 Signal 1 (flow balance) —
  pasture_model.py's net_daily_change_kgDM() and effective_hectares(). REAL, built.
- stocking_ratio: from Group C2 Signal 2 — stock_units.py. REAL, built. Structural
  context only, not scored directly (see design note above).
- price_favourable_signal / price_low_signal: from Group D (price_vs_seasonal, not
  built). If omitted, the stub degrades gracefully to pasture-only scoring, flagged
  in output via `price_data_available`.
- class_transition_penalty: quantifies the lamb->hogget price drop. Hard-set
  placeholder below — FORMULAS.md Group E Open Decision #1, still TBD for a real figure.

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

# --- Flow balance normalization caps — PER REGION (redesigned again 2026-07-17, same
# day, found while testing Auckland end-to-end). A single cap pair — even the
# deficit/surplus-split version above — was still structurally unfair across regions:
# Auckland's real growth curve tops out at 25.91 kg DM/ha/day (its absolute ceiling,
# best possible spring conditions), while a shared surplus cap of 65 was grounded in
# Taranaki's much higher-magnitude spring flush (69.8). That meant Auckland farms could
# NEVER show a strong surplus signal, structurally, regardless of stocking level or
# timing — not a borderline case, a hard ceiling below half the shared cap.
#
# Computed per region from real data: each region's own growth curve min/max
# (pasture_growth_curve.csv) against demand at that region's config.py terrain type's
# min/max SU/ha (terrain_carrying_capacity.csv) x 1.42. Deficit capped uniformly at 12
# across regions (demand-side variation from overstocking isn't structurally bounded by
# "typical" terrain range the way growth is — stocking_ratio can exceed 1 regardless of
# region). Surplus is genuinely region-specific, since that's what the real data shows
# actually varies by ~3x between Auckland and Taranaki.
FLOW_BALANCE_CAPS_BY_REGION = {
    "waikato":  {"deficit": 12.0, "surplus": 48.0},
    "taranaki": {"deficit": 12.0, "surplus": 63.0},
    "auckland": {"deficit": 12.0, "surplus": 20.0},
}

# --- Missing-price-data treatment (redesigned again 2026-07-17, third pass, per
# direct feedback: an arbitrary score penalty has no principled magnitude — 0.10 was
# never defensible as "the right number," just "a number." Missing price data now
# contributes exactly 0 to the score (no penalty, no fill-in guess) and instead
# downgrades CONFIDENCE by one tier. This reuses the same mechanism Group F already
# has for a structurally identical problem — "we have less to go on, so we're less
# sure" — rather than inventing a second, separate penalty knob for the same idea.
#
# Trade-off, stated plainly: this drops the "knowing always scores strictly higher"
# guarantee from the previous design. Missing data and a confirmed worst-case-real
# price now score identically (both contribute 0) — which is correct: neither
# provides positive support for the action. What differs is confidence, not score
# magnitude, because confidence is what actually represents "how sure are we,"
# not the score.
CONFIDENCE_ORDER = ["HIGH", "MEDIUM", "LOW"]


def downgrade_confidence(confidence: str) -> str:
    """
    Steps one tier down (HIGH -> MEDIUM -> LOW), floors at LOW (never goes negative/
    below the scale). Raises ValueError on an unrecognized confidence string rather
    than silently passing it through unchanged.
    """
    if confidence not in CONFIDENCE_ORDER:
        raise ValueError(f"confidence must be one of {CONFIDENCE_ORDER}, got {confidence!r}")
    idx = CONFIDENCE_ORDER.index(confidence)
    return CONFIDENCE_ORDER[min(idx + 1, len(CONFIDENCE_ORDER) - 1)]


def normalize_signal(value: float, cap: float) -> float:
    """
    Clip a raw signal to 0-1 by dividing by a cap and bounding.
    Placeholder normalization — no real distribution analysis behind `cap`
    yet. Negative values clip to 0 (a signal can't be "negatively deficit").
    """
    if cap <= 0:
        raise ValueError(f"cap must be > 0, got {cap}")
    return max(0.0, min(1.0, value / cap))


def pasture_signals_from_flow_balance(region_id: str, net_daily_change_kgDM: float,
                                       effective_hectares: float) -> dict:
    """
    REAL — Group C2 Signal 1 (flow balance), from pasture_model.py's
    net_daily_change_kgDM(). This is what actually drives sell/buy scoring now.

    net_daily_change_kgDM is whole-farm (kg DM/day), so it's normalized per hectare
    here before scoring — a -500 kg DM/day deficit means something very different on
    a 50ha block vs a 500ha farm.

    Caps are PER REGION (see FLOW_BALANCE_CAPS_BY_REGION) — a single shared cap made
    Auckland structurally unable to ever show a strong surplus signal, since its real
    growth ceiling is ~1/3 of Taranaki's. Raises KeyError for an unrecognized region
    rather than silently falling back to a default that would reintroduce that bug.

    <0 -> deficit pressure (pasture shrinking, sell signal)
    >0 -> surplus (buy/hold capacity)
    """
    if effective_hectares <= 0:
        raise ValueError(f"effective_hectares must be > 0, got {effective_hectares}")
    if region_id not in FLOW_BALANCE_CAPS_BY_REGION:
        raise KeyError(
            f"No flow-balance caps for region_id={region_id!r}. Known regions: "
            f"{sorted(FLOW_BALANCE_CAPS_BY_REGION.keys())}. Add an entry to "
            f"FLOW_BALANCE_CAPS_BY_REGION for new regions — don't reuse another "
            f"region's caps, they're grounded in that region's own growth data."
        )
    caps = FLOW_BALANCE_CAPS_BY_REGION[region_id]
    net_per_ha = net_daily_change_kgDM / effective_hectares
    deficit_raw = max(0.0, -net_per_ha)
    surplus_raw = max(0.0, net_per_ha)
    return {
        "pasture_deficit_signal": normalize_signal(deficit_raw, cap=caps["deficit"]),
        "pasture_surplus_signal": normalize_signal(surplus_raw, cap=caps["surplus"]),
        "net_per_ha_kgdm": round(net_per_ha, 2),
        "source": "flow_balance",  # real trend signal, not a structural snapshot
    }


def stocking_ratio_context(stocking_ratio: float | None) -> dict:
    """
    Group C2 Signal 2 — STRUCTURAL context, not scored directly (see module
    docstring for why this is complementary rather than redundant with flow
    balance). Returns a category + note string for `notes`, not a score component.
    """
    if stocking_ratio is None:
        return {"category": None, "note": None}
    if stocking_ratio > 1.0:
        category = "overstocked"
    elif stocking_ratio < 1.0:
        category = "understocked"
    else:
        category = "at_capacity"
    return {
        "category": category,
        "note": f"structural context: stocking_ratio={stocking_ratio:.2f} ({category} "
                f"for land class) — this is a snapshot, not a trend; read alongside "
                f"the flow-balance signal above, not instead of it.",
    }


def score_sell(
    pasture_deficit_signal: float,
    price_favourable_signal: float | None,
    crosses_lamb_hogget_boundary: bool = False,
) -> dict:
    """
    sell_score = W1 * pasture_deficit_signal + W2 * price_favourable_signal
                 - class_transition_penalty

    If price_favourable_signal is None, it contributes 0 — no penalty, no fill-in
    guess. The consequence of missing data (lower confidence) is handled by
    downgrade_confidence() in run_recommendation(), not here.
    """
    price_available = price_favourable_signal is not None
    pasture_component = pasture_deficit_signal * W1_PASTURE
    price_component = (price_favourable_signal or 0.0) * W2_PRICE

    transition_penalty = LAMB_HOGGET_TRANSITION_PENALTY if crosses_lamb_hogget_boundary else 0.0

    raw_score = pasture_component + price_component - transition_penalty

    return {
        "score": round(raw_score, 4),
        "price_data_available": price_available,
        "penalty_applied": transition_penalty,
    }


def score_buy(
    pasture_surplus_signal: float,
    price_low_signal: float | None,
) -> dict:
    """
    buy_score = W1 * pasture_surplus_signal + W2 * price_low_signal
    Same treatment as score_sell() — missing data contributes 0, no penalty.
    """
    price_available = price_low_signal is not None
    pasture_component = pasture_surplus_signal * W1_PASTURE
    price_component = (price_low_signal or 0.0) * W2_PRICE

    raw_score = pasture_component + price_component

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
    region_id: str,
    net_daily_change_kgDM: float,
    effective_hectares: float,
    confidence: str,
    stocking_ratio: float | None = None,
    price_vs_seasonal_pct: float | None = None,
    crosses_lamb_hogget_boundary: bool = False,
) -> ActionCandidate:
    """
    Wires one (class, horizon) pair end-to-end. This is the thin vertical slice:
    net_daily_change_kgDM -> flow-balance signals -> sell/buy scores -> action,
    with stocking_ratio carried alongside as structural context (not scored).
    Loop this over farm_mob x [7, 14, 28] per FORMULAS.md E2 structure.

    region_id is required now (not optional) — flow-balance caps are per-region
    (see FLOW_BALANCE_CAPS_BY_REGION), so there's no safe default to fall back to.
    """
    pasture = pasture_signals_from_flow_balance(region_id, net_daily_change_kgDM, effective_hectares)
    ratio_ctx = stocking_ratio_context(stocking_ratio)

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

    # Confidence downgrade replaces the old score penalty — applies whenever price
    # data is missing, regardless of what action results. This is about how sure we
    # are, not how good the pasture case is.
    final_confidence = confidence if price_vs_seasonal_pct is not None else downgrade_confidence(confidence)

    notes = []
    if not sell["price_data_available"]:
        notes.append(f"price data unavailable — scored on pasture signal only, "
                     f"confidence downgraded {confidence} -> {final_confidence}")
    notes.append(f"flow balance: {pasture['net_per_ha_kgdm']} kg DM/ha/day net "
                 f"(real trend signal, drives this score)")
    if ratio_ctx["note"]:
        notes.append(ratio_ctx["note"])

    return ActionCandidate(
        stock_class=stock_class,
        horizon_days=horizon_days,
        action=action,
        score=final_score,
        confidence=final_confidence,
        price_data_available=sell["price_data_available"],
        notes=notes,
    )


# --- Tests: realistic inputs + deliberate failure cases ---
if __name__ == "__main__":
    # Realistic case 1: pasture tightening (deficit), no price data yet, but
    # structurally understocked (stocking_ratio < 1) — the two signals disagree,
    # which is exactly the case the design note above says to surface, not hide.
    # region_id="taranaki" — deficit cap is uniform (12) across regions, so this
    # would behave the same in any region; taranaki chosen arbitrarily.
    c1 = run_recommendation(
        stock_class="ewes",
        horizon_days=14,
        region_id="taranaki",
        net_daily_change_kgDM=-800,   # recalibrated for the deficit cap (12, was 18)
        effective_hectares=100,
        confidence="MEDIUM",
        stocking_ratio=0.8,           # structurally understocked
    )
    print(c1)
    assert c1.action == "SELL"
    assert c1.price_data_available is False
    assert c1.confidence == "LOW", f"expected MEDIUM downgraded to LOW, got {c1.confidence}"
    assert any("understocked" in n for n in c1.notes)
    assert any("downgraded MEDIUM -> LOW" in n for n in c1.notes)

    # Realistic case 2: pasture surplus, price low vs seasonal -> BUY candidate.
    # region_id="auckland" DELIBERATELY — this is the region whose real surplus cap
    # (20, was wrongly sharing Taranaki's 65) is the whole reason per-region caps
    # exist. Magnitude sized for Auckland's real, much smaller natural range.
    c2 = run_recommendation(
        stock_class="hoggets",
        horizon_days=28,
        region_id="auckland",
        net_daily_change_kgDM=400,
        effective_hectares=90,
        confidence="LOW",
        price_vs_seasonal_pct=-0.12,
    )
    print(c2)
    assert c2.action == "BUY"
    assert c2.confidence == "LOW"  # unchanged — price data was available, no downgrade
    assert not any("stocking_ratio" in n for n in c2.notes)  # correctly omitted

    # Realistic case 3: lamb crossing hogget boundary during a strong sell window,
    # stocking_ratio agrees (overstocked) — both signals point the same way here
    c3 = run_recommendation(
        stock_class="lambs",
        horizon_days=7,
        region_id="taranaki",
        net_daily_change_kgDM=-1200,
        effective_hectares=80,
        confidence="HIGH",
        stocking_ratio=1.3,
        price_vs_seasonal_pct=0.10,
        crosses_lamb_hogget_boundary=True,
    )
    print(c3)
    assert c3.action == "SELL"
    assert c3.confidence == "HIGH"  # unchanged — price data was available
    assert any("overstocked" in n for n in c3.notes)

    # Failure case 1: net_daily_change exactly 0 -> both signals 0 -> HOLD.
    # Confidence still downgrades even though the action is HOLD — missing data
    # affects confidence regardless of what action results.
    c4 = run_recommendation(stock_class="cows", horizon_days=14, region_id="taranaki",
                             net_daily_change_kgDM=0,
                             effective_hectares=100, confidence="MEDIUM")
    assert c4.action == "HOLD"
    assert c4.confidence == "LOW"

    # Failure case 2: bad cap should raise, not silently misnormalize
    try:
        normalize_signal(0.5, cap=0)
        raise AssertionError("expected ValueError on cap=0")
    except ValueError:
        pass

    # Failure case 3: zero/negative effective_hectares should raise, not divide silently
    try:
        pasture_signals_from_flow_balance("taranaki", net_daily_change_kgDM=-100, effective_hectares=0)
        raise AssertionError("expected ValueError on effective_hectares=0")
    except ValueError:
        pass

    # Failure case 4: downgrade_confidence floors at LOW, doesn't error or go negative
    assert downgrade_confidence("HIGH") == "MEDIUM"
    assert downgrade_confidence("MEDIUM") == "LOW"
    assert downgrade_confidence("LOW") == "LOW"
    try:
        downgrade_confidence("nonsense")
        raise AssertionError("expected ValueError on unrecognized confidence")
    except ValueError:
        pass

    # Failure case 5: unrecognized region_id should raise, not silently reuse another
    # region's caps — that would reintroduce the exact bug per-region caps exist to fix
    try:
        pasture_signals_from_flow_balance("nonexistent_region", net_daily_change_kgDM=100,
                                           effective_hectares=50)
        raise AssertionError("expected KeyError for unknown region_id")
    except KeyError:
        pass

    # --- Region-specific cap check: the actual bug that motivated this redesign.
    # Same net_daily_change_kgDM and effective_hectares, different region — Auckland's
    # much smaller real surplus cap (20) should produce a HIGHER normalized signal
    # (closer to saturation) than Taranaki's (63) for an identical raw surplus, because
    # that same absolute surplus represents a much bigger deal in Auckland's real range.
    auckland_signal = pasture_signals_from_flow_balance("auckland", net_daily_change_kgDM=900,
                                                         effective_hectares=50)
    taranaki_signal = pasture_signals_from_flow_balance("taranaki", net_daily_change_kgDM=900,
                                                         effective_hectares=50)
    print(f"Same raw surplus (18 kg DM/ha/day), region-specific signal: "
          f"auckland={auckland_signal['pasture_surplus_signal']}, "
          f"taranaki={taranaki_signal['pasture_surplus_signal']}")
    assert auckland_signal["pasture_surplus_signal"] > taranaki_signal["pasture_surplus_signal"], (
        "expected Auckland's smaller cap to produce a stronger normalized signal for "
        "the same raw surplus — this is the whole point of per-region caps"
    )

    # --- Design demonstration: missing data and worst-case real data (price exactly
    # at seasonal average) now score IDENTICALLY (both contribute 0 to price_component)
    # — that's correct, neither supports the action. What differs is CONFIDENCE: missing
    # data gets downgraded, worst-case real data does not, even though the number is
    # the same. This is the actual point of the redesign — surfaced explicitly here so
    # the trade-off is visible in the test suite, not just in code comments.
    same_pasture_kwargs = dict(stock_class="test", horizon_days=7, region_id="taranaki",
                                net_daily_change_kgDM=2000, effective_hectares=50,
                                confidence="HIGH")
    without_price = run_recommendation(**same_pasture_kwargs)
    with_worst_case_price = run_recommendation(**same_pasture_kwargs,
                                                price_vs_seasonal_pct=0.0)
    assert without_price.score == with_worst_case_price.score, (
        "expected identical scores (both contribute 0 price component) — "
        f"got {without_price.score} vs {with_worst_case_price.score}"
    )
    assert without_price.confidence == "MEDIUM"  # downgraded from HIGH
    assert with_worst_case_price.confidence == "HIGH"  # not downgraded, data was real
    print(f"Same score ({without_price.score}), different confidence: "
          f"missing={without_price.confidence} vs worst-case-real={with_worst_case_price.confidence}")

    # Ranking test: candidates including a HOLD should exclude it from ranking
    ranked = rank_candidates([c1, c2, c3, c4], top_n=2)
    assert c4 not in ranked
    assert len(ranked) == 2
    print("Top actions:", [(c.stock_class, c.horizon_days, c.action, c.score) for c in ranked])

    print("All tests passed.")