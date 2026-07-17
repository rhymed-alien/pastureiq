# FORMULAS REFERENCE — PastureIQ
**The complete formula map the tool works toward. Not all built yet — each is tagged
with its build stage. Help a farmer decide WHEN to buy/sell stock, given pasture supply,
mob feed demand, and market price.**

Status tags: [NOW] definable today · [MP2] Mini-Project 2 (modelling) · [MP3] Mini-Project 3 (forecasting/AI)
Build tags: ✅ BUILT (tested) · 🔶 PARTIAL (built, data incomplete) · — not started

---

## ⚠️ CORRECTIONS LOGGED
1. Daily feed demand per LSU was originally written as "~14.2 kg DM/day" — an arithmetic
   error (off by 10×). Correct figure: **1.42 kg DM/day per LSU** (520 kg DM/year ÷ 365).
2. Group B was originally described as "a trained model (regression/XGBoost)." No labeled
   ground-truth dataset (actual observed pasture growth, dated, by region) exists or was
   found for the three target regions — so nothing can be *trained*. Corrected to what's
   actually buildable: a sourced seasonal curve + a stated, documented (not fitted) weather
   adjustment. See Group B below.
3. Waikato's curve was originally anchored to dairy pasture data (DairyNZ Ruakura) with no
   correction, and West Auckland had no curve at all. Both are now anchored to real,
   farm-type/landform-correct annual totals (Cichota et al. 2014 for Waikato; Auckland
   Council TR2017/020 for West Auckland) — see Group B and the data-sources appendix.
   The monthly *shape* is still a dairy-curve proxy for all three regions; only the
   *magnitude* changed. This is a partial fix, not a full resolution — stated as such below.

Lesson, three times now: verify every number, including ones already written down or already
named in a plan.

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
  Source: RuralHQ (2019); Otago Regional Council memo (2023) citing Parker (1998).
- Per-class LSU values (ewe 1.0, hogget 0.7, ram 0.8, wether 0.7, grazing sheep 0.7, lamb 0.7
  interim, full cattle range) sourced from B+LNZ Sheep & Beef Farm Survey.
  ⚠ CHECK: `stock_units.py` currently hardcodes these as `LSU_VALUES`, not loaded from
  `lsu_conversion_table.csv` — reconcile which is the actual source of truth in your repo.
- **Caveat:** 1.42 kg DM/day is the annual average; real demand is seasonal (higher in
  lactation, lower at maintenance). v1 uses the flat average — flagged, not fixed.
- Lamb feed-side LSU: B+LNZ's survey has no standalone lamb class. Resolved (interim) to
  grazing sheep's 0.7 as nearest class — swap in a real figure if B+LNZ supplies one later.

---

### B. PASTURE SUPPLY — how much feed the land grows  [MP2] 🔶 PARTIAL — `src/pasture_model.py`
*Terrain and region matter here. NOT a trained model (see Correction #2) — a sourced
seasonal baseline, adjusted by a stated weather heuristic.*

```
growth_rate_kgdm_ha_day = seasonal_baseline(region, month) × water_surplus_adjustment
daily_pasture_grown_kgDM = growth_rate_kgdm_ha_day × effective_hectares
```

**Baseline — `data/raw/reference/pasture_growth_curve.csv`. Two layers, not one: monthly
SHAPE and annual MAGNITUDE now come from different sources for two of three regions —
stated explicitly, not blended silently.**

| Region | Annual total (magnitude) | Monthly shape |
|---|---|---|
| South Waikato/King Country | ✅ Cichota et al. (2014) LUC6, sheep/beef APSIM sim, 8493 kg DM/ha/yr | ⚠ Borrowed from DairyNZ Ruakura (dairy) |
| South Taranaki/N. Whanganui | ⚠ DairyNZ Hawera WTARS (dairy), unchanged | ⚠ Same DairyNZ curve (dairy) |
| West Auckland | ✅ Auckland Council TR2017/020 Appendix 2, landform-matched, 6900 kg DM/ha/yr | ⚠ Borrowed from DairyNZ Ruakura (dairy) — a second assumption stacked on the first |

- **Waikato:** DairyNZ Ruakura/Newstead (1996–2017 avg, dairy) still supplies the *shape*
  (relative seasonal pattern), but the curve is now rescaled so its annual total matches
  Cichota et al. (2014) — a real AgResearch APSIM simulation explicitly modelled as
  "rotational grazing of a sheep and beef system" (3-week cuts to 1250 kg DM/ha residual),
  for LUC Class 6 (steep hill) in Waikato specifically. Scale factor 0.4819. First
  genuinely sheep/beef-anchored figure in this project — the dairy caveat now applies to
  shape only, not magnitude, for this region.
- **Taranaki:** unchanged. Cichota et al. (2014) covers only Waikato/Canterbury/Southland;
  TR2017/020 is Auckland-only. No sheep/beef-specific Taranaki source was found this
  session — still fully DairyNZ-proxy, both shape and magnitude. Full dairy-vs-hill-country
  caveat still applies.
- **West Auckland:** previously unresolved entirely (no DairyNZ dataset exists for
  Auckland). Now anchored to TR2017/020 (Hicks & Curran-Cournane, 2017, Auckland Council
  Technical Report 2017/020) Appendix 2 — real field-trial-derived pasture yields by
  landform/geology/management level. Region matched to "regolithic footslope" landform on
  averaged sandstone + mudstone/shale geology (Waitemata Group — the actual terrain under
  the Kumeu/Waimauku/Muriwai lifestyle-block belt), semi-improved management column.
  Shape borrowed from the *original* Waikato dairy curve (no Auckland-specific seasonal
  data exists anywhere found this session) — this stacks two assumptions, not one: flag
  both layers separately in the capstone write-up, don't collapse them into a single
  caveat.
- **Still true for all three regions:** the seasonal *shape* is dairy-derived. Relative
  month-to-month pattern (spring flush, winter trough) likely transfers reasonably across
  farm types; it is the one part of Group B's baseline that has not been corrected this
  round. Revisit if monthly-resolution sheep/beef or hill-country data is ever found —
  Taranaki DTT Stratford (already in your files, see appendix) remains the one candidate
  for a genuinely trained, non-proxy model, flagged for MP3.

**Adjustment — heuristic, not fitted:**
```
water_surplus_adjustment = clip(water_surplus_today / water_surplus_monthly_norm, 0.5, 1.2)
```
Reasoned from Woodward et al.'s described weather→growth relationship, not trained on labeled
data (none exists). `WATER_SURPLUS_ADJUSTMENT_MIN/MAX` in `pasture_model.py`. TODO: calibrate
against farmer feedback — currently a defensible starting assumption, not a measured figure.

**Effective hectares:**
```
effective_hectares = total_hectares − non_grazeable_hectares
```
Total hectares minus non-grazeable land (gorse, bush, bluffs, too-steep faces) — the area that
grows feed for the animals is the area they can graze. Clean definition, farmer-confirmed.

**Terrain enters in three separate places — do not conflate:**
1. AREA → `effective_hectares` above: how much land can be grazed at all.
2. PRODUCTIVITY & ENERGY COST → inside the growth-rate curve above, plus a feed-cost uplift:
   steep country grows less pasture per ha and animals burn more energy grazing it (B+LNZ FS90:
   hard hill cow ~65 MJME/day vs ~55 easy hill; FS83: +0.5 MJME steep sheep). Per-hectare
   productivity / per-animal cost — not area.
3. CARRYING CAPACITY (SU/ha) → Group C2's `stocking_ratio` land-class ceiling. Verified B+LNZ
   ranges: hard hill 2–7 SU/ha · steep hill 6–10 · easier hill 7–13 · high country ≤3.
   `lifestyle_flat` ✅ RESOLVED (2026-07-16): 4.5–15.5 SU/ha, sourced from TR2017/020's
   un-improved/improved bounds (same landform/geology match as the growth curve above) —
   a reasoned proxy, not a site inspection; validate against West Auckland farmer contacts.

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
#   Gives trend, not absolute buffer.

# Signal 2 — CAPACITY RATIO (structural baseline; no cover, no weather) ✅ BUILT:
stocking_ratio = (total_LSU / effective_hectares) / carrying_capacity_SU_per_ha
#   >1 → overstocked for land class · <1 → room to add
#   carrying_capacity_SU_per_ha = midpoint of the terrain's min/max SU/ha range
#   (terrain_carrying_capacity.csv) — decision made in stock_units.py, not previously
#   specified here; revisit if farmer validation suggests midpoint is wrong.
```
- Gives trend (Signal 1) + structural context (Signal 2) without a plate-meter reading.
- Gives up the absolute "X days of feed left" countdown — needs a starting cover level,
  unlocked only when the farmer optionally provides `current_cover`.
- ⚠ UNIT CHECK: assumes SU and LSU are the same ewe-equivalent basis — not yet formally
  confirmed (Open Decision #6).

**`current_cover` — RESOLVED:** tool-estimated is the default and always runs; farmer-entered
`current_cover` is an optional override, not a separate mode. When provided, it replaces the
model's estimate for that session. Output always carries `cover_source`
(`"estimated"` | `"farmer_entered"`) so the farmer knows whether a number is measured or
modelled — same honesty principle as Group F's confidence markers.

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
UI requirement: `cover_source` must surface in `03_pasture_risk.py` (e.g. "(estimated)" vs
"(your entry)" next to the days-of-feed figure).

- ⚠ GAP — cover ESTIMATION method undefined: the above settles WHICH path is default, not HOW
  the estimate is computed. Candidates: carry last-known cover forward + Σ net_daily_change;
  or a regional baseline from the growth model / future NDVI. Not needed for the cover-free
  default — only for the optional countdown path.

- `minimum_residual_cover` — a TERRAIN property, not a single national figure (same logic as
  carrying capacity). Still fully open — all four values TBD:
```
MIN_RESIDUAL_COVER_BY_TERRAIN = {
    "hard_hill": None, "steep_hill": None, "easier_hill": None, "lifestyle_flat": None,
}
```
  Source needed: AgResearch/DairyNZ grazing-residual guidance by terrain class (or B+LNZ if
  held) — same research task as `terrain_carrying_capacity.csv`, not yet done.

- No reconciliation logic planned for farmer-entered vs model-estimated cover diverging
  sharply — MP2 is override-only. Flagging large divergence as a data-quality signal is a
  candidate for MP3/capstone, not required now.

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
- Lamb→hogget boundary is age/dentition based: first adult incisors erupt ~12 months, dropping
  out of premium lamb pricing. Source: ScienceDirect (Hogget overview); B+LNZ; Te Ara. A timing
  constraint, not a breeding-economics model (deliberately out of scope).
- Price data: B+LNZ farmgate prices by class (lamb, mutton, steer, heifer, cow, bull).

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
Highest-scoring class-action leads (e.g. "Sell store lambs" outranks "Hold ewes" if the lamb
score is stronger). Ranking rule (ties, minimum threshold) — TBD, MP2.

**Open in Group E:**
1. Signal variables are names with no defined number/scale yet: `pasture_deficit_signal`,
   `price_favourable_signal`, `pasture_surplus_signal`, `price_low_signal`,
   `class_transition_penalty`. Before coding: `pasture_deficit_signal` ← C2, normalised 0–1;
   `price_favourable_signal` ← D's `price_vs_seasonal`, decide cap/scale;
   `class_transition_penalty` ← quantify the lamb→hogget price drop.
2. Score → action thresholds (SELL/HOLD/BUY cut-offs) — not yet defined.
3. Trade-off list — output spec requires surfaced trade-offs. Known so far: waiting for a
   better price vs the lamb→hogget drop; selling now to relieve pasture vs holding for a price
   rise; buying into surplus pasture vs drought risk over the holding window. Plain-English
   wording is MP3.

---

### F. CONFIDENCE MODEL — anchored to real forecast skill  [NOW ✅ defined, MP2 to apply]
*Not a gut number — anchored to measured weather-forecast skill per horizon.*

| Horizon | Weather basis | Skill (cited) | Confidence |
|---------|---------------|---------------|------------|
| 1 week  | specific daily forecast | ~80–90% (5–7 day range) | HIGH |
| 2 weeks | accumulated totals, not daily | ~14-day skill ceiling; totals still skilful | MEDIUM |
| 4 weeks | 4-week average/trend only | fair skill for averages, driven by weeks 1–2 | LOW / OUTLOOK |

Sources: American Meteorological Society (no useful daily skill beyond ~8 days); Riemer et al.
/ JGU (14-day ceiling, errors double ~every 5 days); Weather Company (~90% at 5d, ~80% at 7d);
S2S hydropower study (4-week average precip retains fair skill).

**Design rule:** the 4-week recommendation must read as a trend/outlook (wetter/drier than
normal), never a daily forecast. Declining confidence with horizon is stated honestly — that
honesty is the feature.

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
- Produces a public accuracy record — farmer trust + portfolio value.
- True adaptive ML (retraining on accumulated data) is a later, optional step; the log is the
  hook that keeps that door open.

---

## WHAT'S DEFINABLE / BUILT vs LATER
- [NOW] Group A ✅, Group C2 Signal 2 ✅ (stocking_ratio), Group F ✅ (structure), Group G ✅
  (log infra, tested).
- [MP2] Group B 🔶 (Waikato + Auckland now anchored to real farm-type/landform-correct
  annual totals; Taranaki still dairy-proxy; monthly shape still dairy-derived for all
  three — see Group B table), Group C/C2 Signal 1 (flow balance — not built), Group E
  logic + structure (not built), Group G application (bias correction not yet applied to
  live predictions).
- [MP3] Group D (price forecast), Group E refinement, bias correction tuning.

## OPEN DECISIONS
1. Cover input method — RESOLVED: tool-estimated default, farmer override optional,
   `cover_source` labelled in output. Cover *estimation formula* (the HOW) still open.
2. `minimum_residual_cover` — CORRECTED SCOPE: per-terrain lookup, not one figure. All four
   values still TBD — separate research task from Group B's growth curve (different table,
   don't conflate).
3. Per-class LSU values — RESOLVED: B+LNZ Sheep & Beef Farm Survey (2026-06-24), national,
   feed-only. ⚠ Verify `lsu_conversion_table.csv` vs `stock_units.py`'s hardcoded dict — see
   flag at top of Group A.
4. Lamb feed-side LSU — RESOLVED (interim): grazing sheep's 0.7, nearest B+LNZ class. Built
   into `stock_units.py`; swap in a real figure if B+LNZ supplies one.
5. Where terrain enters — RESOLVED: `effective_hectares` = grazeable area; productivity/energy
   cost in Group B; carrying capacity is the C2 ceiling.
6. SU vs LSU basis — still open; confirm same ewe-equivalent unit before trusting
   `stocking_ratio` outputs.

## NAMED GAPS
- Cover estimation formula (Group C2) — HOW, not WHICH. Only needed for the optional countdown
  path.
- `MIN_RESIDUAL_COVER_BY_TERRAIN` (Group C2) — all four terrain values, fully open. Note:
  Cichota et al. (2014)'s APSIM cutting residual (1250 kg DM/ha) is a candidate figure for
  hard_hill/steep_hill/easier_hill — not yet formally adopted, flagged here as a lead.
- Taranaki growth curve — still fully dairy-proxy (shape + magnitude); no sheep/beef-specific
  source found this session. The one remaining region with no upgrade.
- Monthly-resolution sheep/beef shape (Group B, all three regions) — magnitude was fixed for
  two regions this session; shape is still borrowed from dairy data everywhere. Taranaki DTT
  Stratford (see appendix) is the one candidate for a genuinely trained replacement, MP3.
- West Auckland landform/geology match (Group B, `terrain_carrying_capacity.csv`) — reasoned
  from coordinates, not site-verified. Validate against West Auckland farmer contacts.
- Dairy-vs-hill-country proxy caveat (Group B) — now applies unevenly (shape-only for
  Waikato/Auckland, full caveat for Taranaki) — needs careful, region-specific wording in the
  capstone methodology write-up, not one blanket statement.
- Water-surplus adjustment calibration (Group B) — 0.5–1.2× clip is reasoned, not fitted or
  validated against farmer feedback yet.
- Group E signal variables — each name needs a defined number + scale before scoring works.
- Group E score→action thresholds and ranking rule (E3).
- Trade-off list (Group E) — enumerate as new ones surface; plain-English wording is MP3.
- Terrain feed-cost uplift figures (Group B) — quantify from B+LNZ FS90/FS83.

## INPUT IMPLICATIONS (feeds PROJECT_SPEC input list)
- Minimum stays: region, total hectares, mob (class + count).
- Optional: `non_grazeable_hectares` (refines effective_hectares, default 0), `current_cover`
  (unlocks countdown), lamb age (hogget guard), liveweights.

---
*Reference sheet v1.4 — Waikato and West Auckland growth curves rescaled to real, farm-type/
landform-correct annual totals (Cichota et al. 2014 sheep/beef APSIM sim for Waikato; Auckland
Council TR2017/020 for West Auckland); `lifestyle_flat` carrying capacity resolved from the
same TR2017/020 source (4.5–15.5 SU/ha); Taranaki unchanged, flagged as the one region still
fully dairy-proxy; monthly shape still dairy-derived for all three regions, stated as a
separate, unresolved layer. Correction #3 logged. Update as decisions resolve.*