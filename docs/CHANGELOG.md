# CHANGELOG.md — PastureIQ

Project-wide change history, pulled out of MRS.md and FORMULAS.md so those documents can
stay lean and current-state-only. Newest first. Entries below are drawn directly from the
version notes already in those two files — nothing added beyond what's documented there.

---

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