# FORMULAS REFERENCE — PastureIQ
**The complete formula map the tool works toward. Functional reference only — current
definitions and values, not the history of how they got here.** Full version history:
`CHANGELOG.md`. Full source citations: `CITATIONS.md`. Full dataset provenance:
`DATA_SOURCES.md`.

Status tags: [NOW] definable today · [MP2] Mini-Project 2 (modelling) · [MP3] Mini-Project 3 (forecasting/AI)
Build tags: ✅ BUILT (tested) · 🔶 PARTIAL (built, data incomplete) · — not started

---

## THE FIVE FORMULA GROUPS

### A. PASTURE DEMAND — how much feed the mob needs  [NOW] ✅ BUILT — `src/stock_units.py`
*The ONLY place LSU is used. LSU = feed demand, nothing else — regional/terrain differences
live in Group B and C2, not here.*

```
total_LSU = Σ (class_count × class_LSU)
daily_feed_demand_kgDM = total_LSU × 1.42        # 520 kg DM/yr ÷ 365
```

- Baseline: 1 LSU = 6000 MJME/year = 520 kg DM/year (modern NZ standard ewe, 55kg + 1 lamb).
- Per-class LSU values (ewe 1.0, hogget 0.7, ram 0.8, wether 0.7, grazing sheep 0.7,
  full cattle range) — source and provenance: `CITATIONS.md` / `DATA_SOURCES.md`.
  ⚠ CHECK: `stock_units.py` currently hardcodes these as `LSU_VALUES`, not loaded from
  `lsu_conversion_table.csv` — reconcile which is the actual source of truth in the repo.
- **Caveat:** 1.42 kg DM/day is the annual average; real demand is seasonal (higher in
  lactation, lower at maintenance). v1 uses the flat average — flagged, not fixed.
- Lamb feed-side LSU: no standalone lamb class exists in the source data. Resolved
  (interim): grazing sheep's 0.7, nearest class — swap in a real figure if one surfaces.

---

### B. PASTURE SUPPLY — how much feed the land grows  [MP2] 🔶 PARTIAL — `src/pasture_model.py`
*Terrain and region matter here. Not a trained model — no labelled ground-truth pasture
growth dataset exists for the three target regions. This is a sourced seasonal baseline,
adjusted by a stated (not fitted) weather heuristic.*

```
growth_rate_kgdm_ha_day = seasonal_baseline(region, month) × water_surplus_adjustment
daily_pasture_grown_kgDM = growth_rate_kgdm_ha_day × effective_hectares
```

**Baseline — `data/raw/reference/pasture_growth_curve.csv`. Monthly shape and annual
magnitude come from different sources for two of three regions — kept explicit, not
blended silently:**

| Region | Annual magnitude | Monthly shape |
|---|---|---|
| South Waikato/King Country | 8493 kg DM/ha/yr (sheep/beef-anchored) | Dairy-curve proxy |
| South Taranaki/N. Whanganui | Dairy-anchored (no sheep/beef source found) | Dairy-curve proxy |
| West Auckland | 6900 kg DM/ha/yr (sheep/beef-anchored) | Dairy-curve proxy |

- Full source detail per region (which study, which scaling factor, which caveats):
  `CITATIONS.md` (Pasture Growth Model section).
- **Still true for all three regions:** the seasonal *shape* is dairy-derived everywhere.
  The relative month-to-month pattern likely transfers across farm types reasonably; it
  is the one part of the baseline not yet upgraded to a sheep/beef source. Taranaki DTT
  Stratford is the one candidate for a genuinely trained replacement — flagged for MP3.

**Adjustment — heuristic, not fitted. Redesigned 2026-07-17 from a ratio to a
difference (see `CHANGELOG.md` for the full story — this wasn't a tuning pass, the
original ratio formula was numerically broken):**
```
deviation = water_surplus_today − water_surplus_monthly_norm
water_surplus_adjustment = clip(1 + deviation/scale × (bound − 1), 0.5, 1.2)
# scale/bound depend on sign: dry (deviation<0) scales toward the 0.5 floor,
# wet (deviation>0) scales toward the 1.2 ceiling — asymmetric on purpose,
# drought suppresses growth more than excess rain boosts it.
```
`WATER_SURPLUS_ADJUSTMENT_MIN/MAX`, `WATER_SURPLUS_DRY_SCALE_MM/WET_SCALE_MM` in
`pasture_model.py`. Scale constants are real 5th/95th percentile deviations sampled
across all three regions (n=5328) — grounded in data, but the MIN/MAX bounds themselves
are still not calibrated against farmer feedback.

⚠ Why this changed: the original ratio (`today/norm`) divides by
`water_surplus_monthly_norm`, which is genuinely negative or near-zero across NZ summer
in every target region (confirmed against real weather data — e.g. Waikato February's
norm is -0.004 mm/day). The old formula's own safety check raised `ValueError` whenever
norm ≤ 0, meaning the pipeline couldn't run in summer at all, not just produced an odd
number. The difference-based version is numerically stable regardless of the norm's
sign.

**Effective hectares:**
```
effective_hectares = total_hectares − non_grazeable_hectares
```
Total hectares minus non-grazeable land (gorse, bush, bluffs, too-steep faces).
Farmer-confirmed definition.

**Terrain enters in three separate places — do not conflate:**
1. AREA → `effective_hectares` above: how much land can be grazed at all.
2. PRODUCTIVITY & ENERGY COST → inside the growth-rate curve above, plus a feed-cost
   uplift not yet quantified into code: steep country grows less pasture per ha and
   animals burn more energy grazing it. Source figures: `CITATIONS.md` (B+LNZ FS90/FS83).
3. CARRYING CAPACITY (SU/ha) → Group C2's `stocking_ratio` land-class ceiling.
   Ranges: hard hill 2–7 SU/ha · steep hill 6–10 · easier hill 7–13 · high country ≤3 ·
   lifestyle_flat 4.5–15.5 (resolved — reasoned proxy, not site-verified; validate
   against West Auckland farmer contacts). Full source: `CITATIONS.md` / `DATA_SOURCES.md`.

---

### C. PASTURE BALANCE — the core signal  [MP2]
*Where demand (A) meets supply (B): "tightening" or "surplus."*

```
net_daily_change_kgDM = daily_pasture_grown_kgDM − daily_feed_demand_kgDM
pasture_cover_forecast(t) = current_cover + Σ(net_daily_change over t days)

# When demand exceeds growth:
days_until_deficit = (current_cover − minimum_residual_cover) /
                     (daily_feed_demand_kgDM − daily_pasture_grown_kgDM)
```

#### C2. Cover-free path (default) [NOW for ratio ✅ BUILT, MP2 for flow]
```
# Signal 1 — FLOW BALANCE (direction + magnitude; no cover needed):
#   net_daily_change_kgDM used directly: <0 → sell pressure; >0 → buy/hold capacity.
#   Gives trend, not absolute buffer. NOT YET BUILT.

# Signal 2 — CAPACITY RATIO (structural baseline; no cover, no weather) ✅ BUILT:
stocking_ratio = (total_LSU / effective_hectares) / carrying_capacity_SU_per_ha
#   >1 → overstocked for land class · <1 → room to add
#   carrying_capacity_SU_per_ha = midpoint of the terrain's min/max SU/ha range
#   (terrain_carrying_capacity.csv) — decision made in stock_units.py.
```
- Gives trend (Signal 1, not built) + structural context (Signal 2, built) without a
  plate-meter reading. Gives up the absolute "X days of feed left" countdown — needs a
  starting cover level, unlocked only when the farmer optionally provides `current_cover`.
- ⚠ UNIT CHECK: assumes SU and LSU are the same ewe-equivalent basis — not yet formally
  confirmed (Open Decision below).

**`current_cover`:** tool-estimated is the default and always runs; farmer-entered
`current_cover` is an optional override, not a separate mode. Output always carries
`cover_source` (`"estimated"` | `"farmer_entered"`).

```python
def calculate_days_of_feed(
    total_lsu: float,
    farm_ha: float,
    growth_rate: float,
    terrain_type: str,                       # selects the residual — see below
    farmer_cover_kgdm: float | None = None,  # optional override
) -> dict:
    """
    Returns {"days_of_feed", "cover_source", "cover_used_kgdm", "residual_used_kgdm"}.
    farmer_cover_kgdm present → cover_source = "farmer_entered".
    Absent → cover derived from the Group B growth model, cover_source = "estimated".
    minimum_residual_cover is looked up by terrain_type — NOT a single national figure.
    """
```
UI requirement: `cover_source` must surface in `03_pasture_risk.py`.

- ⚠ GAP — cover ESTIMATION method undefined: settles WHICH path is default, not HOW the
  estimate is computed. Candidates: carry last-known cover forward + Σ net_daily_change;
  or a regional baseline from the growth model / future NDVI. Only needed for the optional
  countdown path.

- `minimum_residual_cover` — a TERRAIN property, not a single national figure. All four
  values still open:
```
MIN_RESIDUAL_COVER_BY_TERRAIN = {
    "hard_hill": None, "steep_hill": None, "easier_hill": None, "lifestyle_flat": None,
}
```
  Source needed: AgResearch/DairyNZ grazing-residual guidance by terrain class. Cichota et
  al. (2014)'s APSIM cutting residual (1250 kg DM/ha) is a candidate figure for
  hard_hill/steep_hill/easier_hill — not yet formally adopted.

- No reconciliation logic planned for farmer-entered vs model-estimated cover diverging
  sharply — MP2 is override-only. Divergence flagging is an MP3/capstone candidate.

- Output feeds SELL/BUY logic: deficit coming → sell pressure; surplus → buy capacity.

---

### D. MARKET SIGNAL — is the price good  [MP3]
*B+LNZ price data BY CLASS. LSU is not used here.*

```
price_vs_seasonal = (current_price − seasonal_avg_price) / seasonal_avg_price
price_forecast_direction = f(price_history, seasonality)    # Prophet model — MP3

if waiting_period crosses lamb→hogget age boundary:
    apply reclassification_price_drop
```
- Lamb→hogget boundary is age/dentition based: first adult incisors erupt ~12 months,
  dropping out of premium lamb pricing. A timing constraint, not a breeding-economics
  model (deliberately out of scope). Sources: `CITATIONS.md`.
- Price data: B+LNZ farmgate prices by class (lamb, mutton, steer, heifer, cow, bull).
  Status: LIVE — see `DATA_SOURCES.md`.

---

### E. BUY/SELL RECOMMENDATION — the output  [MP2 logic → MP3 refinement]
*Combines C and D. A scoring + ranking system, not one formula.*

```
sell_score = w1 × pasture_deficit_signal + w2 × price_favourable_signal − class_transition_penalty
buy_score  = w1 × pasture_surplus_signal + w2 × price_low_signal
```
- Weights start hand-set, tuned later against the predictions log (Group G).
- Output: ranked list (1–2 actions), each tagged with horizon (1/2/4 wk) and confidence
  (Group F).
- 🔶 PARTIAL — crude stub built and tested in `src/recommendation_engine.py`: placeholder
  weights, placeholder normalization caps, placeholder score→action thresholds. Wires an
  end-to-end path so there's a real ranked output to test against real signals as Groups
  B and D land. Not tuned.

**E2 — structure:** Groups B/C/D/E run once per horizon × once per sellable class.
```
for horizon in [7, 14, 28]:
    for stock_class in farm_mob:
        pasture_signal = balance_signal(horizon)             # per farm
        price_signal   = market_signal(stock_class, horizon) # per class
        sell_score[stock_class][horizon] = score_sell(...)
        buy_score[stock_class][horizon]  = score_buy(...)
# Rank all (class, horizon, action) candidates → top 1–2 → output.
```

**E3 — per-class prioritisation:** rank all candidates by score magnitude; surface top 1–2.
Ranking rule (ties, minimum threshold) — TBD.

**Open in Group E:**
1. Signal variables need defined 0–1 scales before scoring is real: `pasture_deficit_signal`
   (← C2, normalised), `price_favourable_signal` (← D's `price_vs_seasonal`, cap/scale
   TBD), `class_transition_penalty` (lamb→hogget price drop, not yet quantified).
2. Score → action thresholds (SELL/HOLD/BUY cut-offs) — not yet defined; placeholder
   values live in `recommendation_engine.py`.
3. Trade-off list — output spec requires surfaced trade-offs. Known so far: waiting for a
   better price vs the lamb→hogget drop; selling now to relieve pasture vs holding for a
   price rise; buying into surplus pasture vs drought risk over the holding window.
   Plain-English wording is MP3.

---

### F. CONFIDENCE MODEL — anchored to real forecast skill  [NOW ✅ defined, MP2 to apply]
*Not a gut number — anchored to measured weather-forecast skill per horizon. Full sources:
`CITATIONS.md`.*

| Horizon | Weather basis | Confidence |
|---------|---------------|------------|
| 1 week  | specific daily forecast | HIGH (~0.85) |
| 2 weeks | accumulated totals, not daily | MEDIUM (~0.60) |
| 4 weeks | 4-week average/trend only | LOW / OUTLOOK (~0.40) |

**Design rule:** the 4-week recommendation must read as a trend/outlook (wetter/drier than
normal), never a daily forecast. Declining confidence with horizon is stated honestly —
that honesty is the feature.

```
confidence_weather(1wk) ≈ 0.85 · (2wk) ≈ 0.60 · (4wk) ≈ 0.40
# Final action confidence also factors price-forecast confidence (MP3) and data completeness.
```

---

### G. BIAS CORRECTION — the simple "learning" layer  [MP2 infra ✅ BUILT, MP3 application]
*Not ML at first — a transparent error-correction loop. `src/predictions_log.py`, tested.*

```
# 1. Log every prediction when made:
record = {date_made, region, horizon, variable, predicted_value, confidence, target_date}

# 2. When target_date arrives, back-fill the outcome:
record.actual_value = observed_value
record.error = predicted_value − actual_value

# 3. Running bias per region + variable + horizon:
bias = mean(error over last N matured predictions)   # refuses to run if fewer than N exist

# 4. Apply correction to future raw predictions (MP3, not built yet):
corrected_prediction = raw_prediction − bias
```
- A measured, self-correcting track record without complex ML.
- True adaptive ML (retraining on accumulated data) is a later, optional step; the log is
  the hook that keeps that door open.

---

## STATUS SUMMARY
- [NOW] Group A ✅, Group C2 Signal 2 ✅ (stocking_ratio), Group F ✅ (structure), Group G ✅
  (log infra, tested).
- [MP2] Group B 🔶 (Waikato + Auckland anchored to sheep/beef sources; Taranaki still
  dairy-proxy; monthly shape still dairy-derived everywhere), Group C/C2 Signal 1 (flow
  balance — not built), Group E 🔶 (crude stub built, not tuned), Group G application
  (bias correction not yet applied to live predictions).
- [MP3] Group D (price forecast), Group E refinement, bias correction tuning.

## OPEN DECISIONS
1. Cover input method — RESOLVED: tool-estimated default, farmer override optional,
   `cover_source` labelled in output. Cover *estimation formula* (the HOW) still open.
2. `minimum_residual_cover` — per-terrain lookup, not one figure. All four values TBD.
3. Per-class LSU values — RESOLVED, national, feed-only. ⚠ Verify
   `lsu_conversion_table.csv` vs `stock_units.py`'s hardcoded dict.
4. Lamb feed-side LSU — RESOLVED (interim): grazing sheep's 0.7.
5. Where terrain enters — RESOLVED: `effective_hectares` = grazeable area;
   productivity/energy cost in Group B; carrying capacity is the C2 ceiling.
6. SU vs LSU basis — still open; confirm same ewe-equivalent unit before trusting
   `stocking_ratio` outputs.

## NAMED GAPS
- Cover estimation formula (Group C2) — HOW, not WHICH.
- `MIN_RESIDUAL_COVER_BY_TERRAIN` (Group C2) — all four terrain values, fully open.
- Taranaki growth curve — still fully dairy-proxy (shape + magnitude).
- Monthly-resolution sheep/beef shape (Group B, all three regions) — shape still borrowed
  from dairy data everywhere.
- West Auckland landform/geology match (Group B) — reasoned, not site-verified.
- Water-surplus adjustment MIN/MAX bounds (Group B) — the formula itself is now
  numerically sound and data-grounded (see Group B section above), but the 0.5/1.2
  bounds are still reasoned, not fitted against real farmer-observed outcomes.
- Group E signal variables — each needs a defined number + scale before scoring is real.
- Group E score→action thresholds and ranking rule (E3).
- Trade-off list (Group E) — enumerate as new ones surface; plain-English wording is MP3.
- Terrain feed-cost uplift figures (Group B) — quantify from B+LNZ FS90/FS83.

## INPUT IMPLICATIONS (feeds PROJECT_SPEC input list)
- Minimum stays: region, total hectares, mob (class + count).
- Optional: `non_grazeable_hectares` (refines effective_hectares, default 0),
  `current_cover` (unlocks countdown), lamb age (hogget guard), liveweights.

---
*Reference sheet v1.5 — streamlined to a functional formula reference. Correction history,
version notes, and source-provenance narrative moved to `CHANGELOG.md` and `CITATIONS.md`.
Update this document's values/formulas as decisions resolve; log the *why* and *when* in
`CHANGELOG.md`, not here.*