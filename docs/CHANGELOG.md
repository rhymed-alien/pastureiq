# CHANGELOG.md — PastureIQ

Project-wide change history, pulled out of MRS.md and FORMULAS.md so those documents can
stay lean and current-state-only. Newest first. Entries below are drawn directly from the
version notes already in those two files — nothing added beyond what's documented there.

---

## pasture_growth_curve.csv — West Auckland shape upgraded from placeholder to real (2026-07-17)

- Replaced West Auckland's flat 12-way-split placeholder with a combined real shape:
  Welsford (Auckland region, Rodney District, 2002-2003) for Jan-Mar/Oct-Dec, Northland
  kikuyu (2016, "196" dataset only) for Jun-Jul, both sources averaged for the
  Apr/May/Aug/Sep overlap. Every month now has at least one real source — no months
  guessed or interpolated.
- A related kikuyu dataset ("228," grazing rotation length study, 1982-84) was
  investigated and explicitly excluded: its date ranges span 4-5 months per row, so
  bucketing it by start-month (as an earlier pass in this session did) mixed
  multi-month rotation-treatment values into single-month buckets — not valid monthly
  data. Caught before being wired into the CSV.
- Rescaled onto TR2017/020's 6900 kg DM/ha/yr magnitude (unchanged, already real).
  Reconstructed annual total from the rescaled monthly values checked against the target
  (6900 both ways).
- Caveat carried into the CSV itself: Welsford (2002-03) and kikuyu (2016) are ~14 years
  apart — flagged as a magnitude-comparability risk, lower risk for the seasonal shape
  actually used, and moot regardless since TR2017/020 remains the magnitude anchor.
- Full detail: `DATA_SOURCES.md`, Pasture Growth section.
- Waikato and Taranaki unchanged in this pass.

## pasture_growth_curve.csv — Waikato shape upgraded from placeholder to real (2026-07-17)

- Replaced Waikato's flat 12-way-split placeholder with a real monthly shape: "Pasture
  Plan growth rate 2002-2003 (King Country)," agyields.co.nz, Paddock Flat + Paddock Oat.
  Rescaled onto Cichota et al. (2014)'s 8493 kg DM/ha/yr magnitude (more robust, 30-year
  simulated figure) via `rescale_shape_to_magnitude()` in `build_pasture_growth_curve.py`.
  Reconstructed annual total from the rescaled monthly values checked against the target
  (8493 both ways).
- Caveat carried into the CSV itself, not just this log: the King Country source is a
  single season (2002-2003), two paddocks — real, but not multi-year-verified. Flagged
  in the `shape_confidence` column.
- Full detail: `DATA_SOURCES.md`, Pasture Growth section.
- Taranaki and Auckland unchanged in this pass.

## Pasture growth sourcing — fabrication found and corrected (2026-07-17)

- A past session's `pasture_growth_curve.csv` cited "DairyNZ Ruakura/Newstead" and
  "DairyNZ Hawera WTARS" as the monthly-shape sources for Waikato, West Auckland, and
  Taranaki. Neither document exists anywhere in this project. The Taranaki entries
  additionally claimed to be "cross-confirmed against DairyNZ Facts and Figures PDF" — a
  verification that never happened. Confirmed by checking every uploaded/held document
  against these claims: no match.
- Real replacements sourced and verified against source PDFs/CSVs the same day:
  - Taranaki: DTT Stratford (Dairy Trust Taranaki), 10 years of real monthly data via
    agyields.co.nz — now the primary Taranaki source, magnitude and shape both.
  - West Auckland: Cichota (2014)/TR2017-derived magnitude unchanged (already real);
    Northland kikuyu data (agyields.co.nz) proposed as a real, species-matched shape
    proxy, replacing the fabricated Waikato-dairy-shape borrow. Adoption pending decision.
  - Waikato: Cichota (2014) Table 2 unchanged as primary (already real, re-verified);
    Reardon (1978) Te Kuiti/Whatawhata beef data added as an independent secondary
    cross-check.
  - Two more real secondary cross-checks added for the Taranaki/Whanganui region:
    Ballantrae (López et al. 2003) and Fielding "Pasture Plan" 2002–2003.
- Full detail: `DATA_SOURCES.md`, Pasture Growth section. `pasture_growth_curve.csv`
  itself still needs rebuilding on this corrected basis — not done as part of this entry.

## FORMULAS.md v1.5 — streamlined to a pure functional reference (2026-07-17)

- Removed the "CORRECTIONS LOGGED" narrative block and the closing meta-lesson
  ("verify every number, including ones already written down or already named in a
  plan") from the top of the document — the corrected values themselves are unchanged
  and still stated in each formula group; only the diary-style explanation of *how* they
  were caught was removed. See the v1.4-and-earlier entries below for that history.
- Group B's per-region sourcing narrative (why each curve was re-anchored, landform
  matching reasoning, "first genuinely sheep/beef-anchored figure" commentary) condensed
  to a values-only table; full reasoning preserved in `CITATIONS.md`.
- Group C2/E/F source lists trimmed to pointers — `CITATIONS.md` is now the single home
  for bibliography, `FORMULAS.md` no longer restates it.
- No formula, value, or open decision was changed in this pass — this was a
  documentation-only cleanup, not a methodology update.

## MRS.md v1.3 — documentation cleanup (2026-07-17)

- B+LNZ price data status corrected: resolved, supplied directly by B+LNZ (same channel
  as the LSU table), not the "in progress" status MRS v1.2 described. Verified in
  `01_weather_and_market_eda.ipynb`.
- Citations register and version history split out into `CITATIONS.md` and
  `CHANGELOG.md` — MRS.md now points to them instead of restating content.
- `DATA_SOURCES.md` rebuilt as a full dataset register (was placeholder-only).
- Priority tags recalibrated: 🔴 now means "blocking work this sprint," not "was needed
  at some point." NIWA licence reply, `FARMER_DECISIONS.md`, and the Streamlit app pages
  (01/02) downgraded from 🔴 to 🟡 — nothing is currently stalled on any of them.
- `src/recommendation_engine.py` added to Section 6.2 tracking — a crude Group E scoring
  stub, built and tested this cycle (see FORMULAS.md Group E and Status Summary).
- Section 7.1 (MP1 notebook) left untouched by request — MP1 is graded and submitted;
  that section is a frozen historical record, not a live tracking item, even where it no
  longer matches the actual combined notebook structure.

---

## FORMULAS.md v1.4 (prior to streamlining)

- Waikato and West Auckland pasture growth curves rescaled to real, farm-type/
  landform-correct annual totals: Cichota et al. (2014) sheep/beef APSIM simulation for
  Waikato; Auckland Council TR2017/020 for West Auckland.
- `lifestyle_flat` carrying capacity resolved (2026-07-16): 4.5–15.5 SU/ha, sourced from
  TR2017/020's un-improved/improved bounds — same landform/geology match as the growth
  curve. Flagged as a reasoned proxy, not a site inspection.
- Taranaki growth curve unchanged — flagged as the one region still fully dairy-proxy
  (both shape and magnitude).
- Monthly shape still dairy-derived for all three regions — stated as a separate,
  unresolved layer, not blended into the magnitude fix.

## FORMULAS.md — corrections logged (undated, pre-v1.4)

- Waikato and West Auckland pasture growth curves rescaled to real, farm-type/
  landform-correct annual totals: Cichota et al. (2014) sheep/beef APSIM simulation for
  Waikato; Auckland Council TR2017/020 for West Auckland.
- `lifestyle_flat` carrying capacity resolved (2026-07-16): 4.5–15.5 SU/ha, sourced from
  TR2017/020's un-improved/improved bounds — same landform/geology match as the growth
  curve. Flagged as a reasoned proxy, not a site inspection.
- Taranaki growth curve unchanged — flagged as the one region still fully dairy-proxy
  (both shape and magnitude).
- Monthly shape still dairy-derived for all three regions — stated as a separate,
  unresolved layer, not blended into the magnitude fix.

## FORMULAS.md — corrections logged (undated, pre-v1.4)

1. Daily feed demand per LSU corrected from an erroneous "~14.2 kg DM/day" (10× arithmetic
   error) to the correct **1.42 kg DM/day per LSU** (520 kg DM/year ÷ 365).
2. Group B corrected from "a trained model (regression/XGBoost)" to what's actually
   buildable: no labelled ground-truth pasture-growth dataset exists for the three target
   regions, so nothing can be trained. Replaced with a sourced seasonal baseline + a
   stated, documented (not fitted) weather adjustment.
3. Waikato's growth curve was originally anchored to dairy pasture data (DairyNZ Ruakura)
   with no correction, and West Auckland had no curve at all. Both re-anchored to real
   farm-type/landform-correct annual totals (see v1.4 entry above). Monthly shape remains
   a dairy-curve proxy for all three regions — magnitude changed, shape did not.

---

## MRS.md v1.2 (2026-07, reconciled against B+LNZ reply 2026-06-24 and MP1 progress)

- Section 2.1: LSU conversion table built from B+LNZ Sheep & Beef Farm Survey data. Beef
  cow LSU corrected 5.8 → 5.5 (national/feed-only basis; the terrain effect previously
  folded into 5.8 moved to the carrying-capacity modifier instead). Hogget corrected
  1.0 → 0.7. Full sheep + cattle + dairy-grazer classes added. The 4.4-vs-5.8 discrepancy
  (RuralFind vs earlier project estimate) resolved in favour of the B+LNZ survey figure.
- Section 1.3: added `docs/blnz_lsu_source_record.md`; DATA_SOURCES.md updated to log
  B+LNZ LSU data and a placeholder for B+LNZ price data.
- Section 3.1: noted MP1 notebook loads weather CSVs directly (SQLite/`database.py`
  deferred, not needed for MP1).
- Section 4.1: B+LNZ farmgate price data — reply received from B+LNZ Economic Service,
  data supply in progress on their side at time of writing. ⚠ **Needs reconciling against
  current repo state** — later notes suggest a price CSV may since have been delivered;
  confirm actual status before treating either version as current.
- Section 4.2 / 4.4: MPI SOPI and Stats NZ Infoshare verified as live, free, accessible
  sources. B+LNZ Stock Number Survey and Lamb Crop Report added (copyright-restricted,
  citation permission pending). Dead ends logged: NZ Meat Board (redirects to B+LNZ, not
  independent), Rabobank (PDF commentary only, no raw data).
- Section 6.1: `stock_units.py` LSU values now sourced from B+LNZ rather than hardcoded
  estimates. `database.py` re-tagged from blocker to MP2-conditional (CSV sufficient for
  MP1).
- Section 7.1: Notebook 01 (weather EDA) status set to partial/substantially-built; soil
  moisture content removed (dropped from the weather pull — see Section 3.1 history);
  three numbered questions, feature engineering (GDD, water surplus, rolling ET0), and a
  two-sample t-test added. Notebooks 02 (market price) and 03 (regional comparison)
  re-tagged from MP1 scope to MP2 lead-in — MP1 deliverable narrowed to notebook 01 only
  ("Option A" scoping decision).
- Section 8: soil-moisture references removed from the dashboard spec (no soil source
  exists yet — see Section 4.3 research task).

## MRS.md v1.1 (reconciliation, retained note only — no full entry list preserved)

- Cross-checked against PROJECT_SPEC.md and FORMULAS.md. Authority split established:
  PROJECT_SPEC.md is authoritative on goal/inputs-outputs/formulas; MRS.md is authoritative
  on files-to-build and build sequence.
- LSU pending-flags closed: Open Decision #3 (per-class LSU values) resolved; Open
  Decision #4 (lamb feed-side LSU) partially resolved (interim: grazing sheep 0.7).

---

## Resolved during documentation cleanup (2026-07-17)

- B+LNZ farmgate price data status — RESOLVED. `blnz_farmgate_prices.csv` was supplied
  directly by B+LNZ (same channel as the LSU table), not the "in progress" public-page
  pull described in MRS v1.2. Row counts/date range/missing-value verification confirmed
  done in `01_weather_and_market_eda.ipynb`. DATA_SOURCES.md corrected.

## Open items carried forward (not yet resolved, tracked once — in FORMULAS.md Open
## Decisions, not duplicated here)

- `minimum_residual_cover` per-terrain values (3 of 4 terrain types still `None`).
- SU vs LSU basis formal confirmation.
- Taranaki pasture growth curve — no sheep/beef-specific source found yet.
- Group E signal scaling and score→action thresholds — placeholder values only
  (see `src/recommendation_engine.py`, added as a stub, not yet tuned).

---
*Changelog v1.0 — extracted from MRS.md and FORMULAS.md version notes. Add new entries
here going forward instead of appending change logs to the working documents themselves.*