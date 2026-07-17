# MASTER REFERENCE CHECKLIST
## PastureIQ — NZ Farm Pasture & Market Decision Tool
**Version:** 1.3 | **Date:** July 2026 | **Deadline:** October 22 2026

> **v1.3 update:** documentation cleanup pass. B+LNZ price data status corrected (was
> showing "in progress" — actually resolved, supplied directly by B+LNZ). Citations
> register and version history moved out of this document into `CITATIONS.md` and
> `CHANGELOG.md` — this file now points to them instead of restating their content.
> `DATA_SOURCES.md` rebuilt as a full register (was placeholder-only). Priority tags
> recalibrated: 🔴 now means "blocking work in front of you right now," not "was needed
> at some point." Full change history: see `CHANGELOG.md`.
>
> **Authority split (unchanged since v1.1):** where this checklist and PROJECT_SPEC
> disagree, PROJECT_SPEC is authoritative on goal/IO/formulas; this checklist is
> authoritative on files-to-build and sequence. FORMULAS.md is authoritative on
> definitional/methodology decisions — open decisions are tracked there once, not
> duplicated here.

---

## HOW TO USE THIS DOCUMENT

- Work through each section in order
- Tick items off as you acquire or create them
- Items marked 🔴 are blockers — something you'd try to do *this sprint* cannot proceed
  without them
- Items marked 🟡 are needed before a specific mini-project, but nothing is blocked on
  them today
- Items marked 🟢 are nice-to-have or capstone polish items
- Every data file needs a corresponding entry in `DATA_SOURCES.md` before you use it
- Every cited source needs an entry in `CITATIONS.md` before you rely on it
- `[x]` = done & verified · `[ ]` = not yet · `[~]` = partially done / pending an external reply
---

## SECTION 1 — PROJECT INFRASTRUCTURE
*Set up once, never redo. All of this belongs in Week 1. Kept 🔴 for historical accuracy
even though it's all done — nothing here is currently at risk.*

### 1.1 Repository & environment
- [x] 🔴 GitHub repository created (public — github.com/rhymed-alien/pastureiq)
- [x] 🔴 Folder structure created:
```
  /data/raw/weather/
  /data/raw/market/
  /data/raw/census/
  /data/raw/reference/
  /data/raw/satellite/      (reserved — Sentinel-2 NDVI, empty for now)
  /data/processed/
  /data/predictions/        (predictions log for cross-check + bias correction; see PROJECT_SPEC)
  /notebooks/
  /src/
  /app/
  /docs/
  /docs/licensing/
```
- [x] 🔴 `.gitignore` file (excludes: `.env`, `__pycache__`, `*.sqlite`, venv/, satellite/)
- [x] 🔴 `README.md` — project title, name, description, setup instructions
- [x] 🔴 `requirements.txt` — packages listed (anthropic + prophet commented out for now)
- [x] 🔴 Python virtual environment set up locally (venv)
- [x] 🔴 `config.py` — code source of truth for regions, paths, settings

### 1.2 Legal & licensing
- [x] 🔴 Email sent to NIWA (data@niwa.co.nz) — student capstone, non-commercial, portfolio use (follow-up scheduled)
- [~] 🟡 NIWA written reply saved to `/docs/licensing/niwa_licence_confirmation.pdf`
  — PENDING, no data currently depends on this (NIWA outlooks are contextual only, not
  used in calculations). Downgraded from 🔴: nothing is blocked while this is open.
- [x] 🔴 Open-Meteo attribution text saved to `/docs/licensing/openmeteo_attribution.txt`
  - Text required: "Weather data from Open-Meteo.com (CC BY 4.0)"
  - NOTE: free Open-Meteo API = non-commercial use only; the DATA is CC BY 4.0. Record both.
- [~] 🟡 B+LNZ terms / use permission — B+LNZ Economic Service supplied LSU AND price data
  directly for this free non-commercial student project, crediting acknowledged. Still to
  do: save a short note confirming citation permission for their *published reports*
  (Stock Number Survey, Lamb Crop Report — separate from the raw data supply) to
  `/docs/licensing/blnz_terms.txt`.
- [ ] 🟡 Stats NZ Crown copyright acknowledgement saved to `/docs/licensing/statsnz_crown_copyright.txt`

### 1.3 Core documentation files
- [x] 🔴 `DATA_SOURCES.md` — full register of every dataset used, planned, or dead-ended.
  Rebuilt in full — see the file itself, not restated here.
- [x] 🔴 `CITATIONS.md` — full bibliography of every source cited in formulas/methodology.
  New this cycle — see the file itself, not restated here.
- [x] 🔴 `CHANGELOG.md` — project-wide version history, pulled out of MRS/FORMULAS. New
  this cycle.
- [~] 🟡 `FARMER_DECISIONS.md` — the 5 decisions the app must support (STARTED: stub created).
  Downgraded from 🔴: no downstream code work is currently blocked on this being complete.
- [x] 🔴 `docs/PROJECT_SPEC.md` — goal, inputs, outputs, scope, infrastructure, build status
- [x] 🔴 `docs/FORMULAS.md` — complete formula reference, Groups A–G incl. bias correction
- [x] 🔴 `docs/blnz_lsu_source_record.md` — verbatim B+LNZ email + LSU table + provenance
- [ ] 🟡 `data_quality.md` — gaps, anomalies, missing stations flagged after EDA
- [ ] 🟡 `FEP_DISCLAIMER.md` — one-paragraph note on Farm Environment Plans
  - "This app provides pasture management guidance based on weather and carrying capacity.
     It does not replace or constitute a Farm Environment Plan. Refer to your regional
     council for regulatory stocking rate requirements."
- [ ] 🟢 `METHODOLOGY.md` — full scientific write-up for capstone submission
---

## SECTION 2 — REFERENCE DATA
*Static files. Download once. Never changes. Lives in `/data/raw/reference/`*

### 2.1 Stock unit standards
- [x] 🔴 `lsu_conversion_table.csv` — NZ Livestock Stock Unit conversion factors (FEED-ONLY, national; terrain NOT here)
  - Built from B+LNZ Sheep & Beef Farm Survey standard conversions, supplied directly by
    B+LNZ Economic Service. Full provenance: `docs/blnz_lsu_source_record.md`, full
    citation: `CITATIONS.md`.
  - ⚠ USE THE `stock_units` COLUMN for feed maths — NOT `cattle_equivalent`.
  - ⚠ CHECK: `stock_units.py` currently hardcodes these as `LSU_VALUES`, not loaded from
    this CSV — reconcile which is the actual source of truth.
- [ ] 🔴 `terrain_carrying_capacity.csv` — NZ carrying capacity by terrain type (THIS is
  where terrain lives). Still not built — genuinely blocking Group C2 and Group E work.
  - Source: B+LNZ farm class benchmarks — see `DATA_SOURCES.md` for the full entry
  - Columns needed: terrain_type, min_su_per_ha, max_su_per_ha, notes
  - Verified ranges: hard hill 2–7 SU/ha · steep hill 6–10 · easier hill 7–13 ·
    high country ≤3 · lifestyle_flat 4.5–15.5 (TR2017/020-sourced, reasoned proxy —
    validate against West Auckland farmer contacts)

### 2.2 Region reference data
- [x] 🔴 `regions.csv` — your three target regions (REFERENCE/documentation layer)
  - config.py holds the region coords the CODE runs on; regions.csv is the richer
    REFERENCE file (rainfall, sunshine, farm class). config.py wins if they ever differ.
  - Region 1: South Waikato / King Country — lat: -38.34, lon: 175.16 (Te Kūiti area)
  - Region 2: South Taranaki / N. Whanganui hill country — lat: -39.63, lon: 174.93
  - Region 3: West Auckland lifestyle blocks — lat: -36.90, lon: 174.52
- [x] 🟡 `blnz_farm_classes.csv` — B+LNZ farm class reference table
  - Columns: class_id, name, su_per_ha_min, su_per_ha_max, terrain_description, typical_ha_range

### 2.3 Scientific citations register
- [x] 🔴 See `CITATIONS.md` — every paper, report, and fact sheet cited in the project,
  grouped by which formula group it supports. Do not restate the bibliography here; add
  new sources to that file directly.
---

## SECTION 3 — WEATHER DATA
*Dynamic. Pulled via API. Stored in `/data/raw/weather/`*

### 3.1 Historical weather — Open-Meteo ERA5  [DONE & VERIFIED]
- [x] 🔴 `weather_waikato.csv` + `.json` — South Waikato 2015–2026 (4177 rows, 0 missing)
- [x] 🔴 `weather_taranaki.csv` + `.json` — South Taranaki 2015–2026 (4177 rows, 0 missing)
- [x] 🔴 `weather_auckland.csv` + `.json` — West Auckland 2015–2026 (4177 rows, 0 missing)
  - Full source detail, licence, and variable list: `DATA_SOURCES.md`
  - ⚠ SOIL VARIABLES REMOVED — caused a 400 error on the ERA5 archive endpoint. Soil
    sourcing is a research task (Section 4.3), not part of this pull.
  - Pulled via `src/pull_weather.py` (loops all regions from config.py), run
    `python -m src.pull_weather`
  - NOTE: notebook 01 loads these CSVs DIRECTLY (no SQLite — `database.py` deferred).

### 3.2 Weather forecast — Open-Meteo live
- [ ] 🟡 `get_forecast_weather()` in `src/pull_weather.py` — 7-day forecast, called live in
  the dashboard on page load. No consumer until the dashboard is built (MP2) — not
  currently blocking anything.

### 3.3 Seasonal climate outlooks — NIWA (subject to licence confirmation)
- [ ] 🟢 NIWA seasonal outlook PDFs — contextual background only, not used in
  calculations. Condition: only if NIWA licence confirms non-commercial use is permitted.
---

## SECTION 4 — MARKET PRICE DATA
*Semi-static. Download monthly. Lives in `/data/raw/market/`*

### 4.1 B+LNZ farmgate prices — primary market dataset
- [x] 🔴 `blnz_farmgate_prices.csv` — RESOLVED. Supplied directly by B+LNZ Economic
  Service (same direct-request channel as the LSU table), delivered as an MP1 output.
  Row counts/date range/missing-value verification done in
  `01_weather_and_market_eda.ipynb`. Full entry: `DATA_SOURCES.md`.

### 4.2 MPI slaughter statistics
- [ ] 🟡 `mpi_slaughter_stats_raw.xlsx` — verified live 2026-06-24, not yet pulled. Useful
  as a supply-side correlation check against price once Group D scoring exists to test
  it against — not a current blocker. Full entry: `DATA_SOURCES.md`.

### 4.3 Soil data — RESEARCH TASK (parked after Open-Meteo soil proved unreliable)
- [ ] 🟡 Research + compare trustworthy NZ soil moisture / soil temperature sources before
  building soil into the model. Candidates and decision criteria: `DATA_SOURCES.md` /
  original research note. Decision to record: which soil source (if any) enters the
  model, or proxy soil from rainfall + ET0 instead.

### 4.4 Alternative NZ livestock data — VERIFIED
- [ ] 🟡 Stats NZ Infoshare (Livestock Slaughtering Statistics), MPI SOPI data — both
  verified live, not yet pulled. Full entries: `DATA_SOURCES.md`.
- [x] 🟢 B+LNZ Stock Number Survey + Lamb Crop Report 2025 — HELD (PDFs uploaded).
  Citation permission — see Section 1.2. Full entry: `DATA_SOURCES.md`.
- [x] 🟢 Dead-ends logged (do not re-chase): NZ Meat Board, Rabobank. Full entries:
  `DATA_SOURCES.md`.

### 4.5 USDA GAIN reports — NZ livestock (optional validation)
- [ ] 🟢 Not yet requested/pulled. Full entry: `DATA_SOURCES.md`.
---

## SECTION 5 — FARM POPULATION & CENSUS DATA
*Static. Download once. Lives in `/data/raw/census/`*

- [ ] 🟡 `statsnz_agcensus_2022_regional.xlsx` — farm count and livestock numbers per
  region, documentation context. Full entry: `DATA_SOURCES.md`.
- [ ] 🟡 `statsnz_livestock_slaughter_timeseries.xlsx` — long-run seasonal patterns.
  Full entry: `DATA_SOURCES.md`.
- [ ] 🟢 `mpi_lifestyle_block_analysis_2024.pdf` — lifestyle block size justification.
  Full entry: `DATA_SOURCES.md`.
---

## SECTION 6 — PYTHON SOURCE FILES
*Lives in `/src/`. Each file is a standalone module with a docstring citing its data sources.*

### 6.1 Core modules — Mini-project 1
- [x] 🔴 `src/stock_units.py`  (FEED-ONLY — terrain does NOT belong here)
  - `LSU_VALUES` dictionary, `calculate_total_lsu()`, `daily_feed_demand_kgDM()`
  - ⚠ terrain NOT here — lives in carrying capacity (Section 2.1)
  - ⚠ decide lamb feed-side treatment — RESOLVED (interim): grazing sheep's 0.7, nearest
    B+LNZ class. See FORMULAS.md Open Decision #4.
- [~] 🔴 `src/pull_weather.py`  (DONE for historical)
  - STILL TO ADD: `get_forecast_weather(lat, lon)` — deferred to dashboard/MP2
- [ ] 🟡 `src/database.py`  (DEFERRED — MP1 runs on CSV, not SQLite)
  - Build when the dashboard or price data needs a query layer, not before.
- [x] 🔴 ~~`src/regions.py`~~ — SUPERSEDED. config.py is the code source of truth.

### 6.2 Analysis modules — Mini-project 2
- [ ] 🟡 `src/pasture_model.py`
  - `estimate_pasture_growth_rate(temp, rainfall, soil_moisture, et0)` — weather to kg DM/ha/day
  - `calculate_days_of_feed(total_lsu, farm_ha, growth_rate)` — forward pasture cover estimate
  - `classify_pasture_risk(days_of_feed, season)` — returns GREEN / AMBER / RED
  - Docstring: cite Woodward et al. — see `CITATIONS.md`
- [ ] 🟡 `src/market_model.py`
  - `get_seasonal_average(species, month)`, `classify_price_signal(...)`,
    `generate_sell_signal(...)`
- [x] 🟡 `src/recommendation_engine.py` — crude Group E scoring stub, built and tested this
  cycle. Hand-set weights (not tuned), placeholder thresholds, degrades gracefully when
  price data isn't wired in yet. Wires an end-to-end path so there's a real ranked
  SELL/HOLD/BUY output to test against — swap in real signals from `pasture_model.py`
  (flow balance) and `market_model.py` (price_vs_seasonal) as they land. See file
  docstring for exactly what's placeholder vs real.

### 6.3 Forecasting modules — Mini-project 3
- [ ] 🟡 `src/price_forecast.py` — Prophet model for farmgate price direction. See
  `CITATIONS.md` (Taylor & Letham, 2018).
- [ ] 🟡 `src/plain_english.py` — calls Anthropic API with model outputs as structured
  input, returns 2-sentence plain-English recommendation.

### 6.4 Utility modules
- [ ] 🟡 `src/data_loader.py` — load/clean each raw file, standardise formats
- [ ] 🟢 `src/fep_alerts.py` — regional rainfall threshold alert (Taranaki, hard-coded)

### 6.5 Prediction logging & confidence
- [x] 🟡 `data/predictions/predictions_log.csv` — schema:
  `date_made, region, horizon_days, variable, predicted_value, confidence, target_date, actual_value, error`
- [x] 🟡 `src/predictions_log.py` — `log_prediction()`, `mature_predictions()`,
  `compute_bias()`, `apply_bias_correction()`
- [x] 🟡 Confidence model (config.py + applied in recommendation logic) — 7/14/28 day
  horizons, HIGH/MEDIUM/LOW confidence. Sources: `CITATIONS.md`.
---

## SECTION 7 — NOTEBOOKS
*Lives in `/notebooks/`. Every notebook has a markdown cell at the top explaining its purpose in plain language.*

> **Note on 7.1:** MP1 has been graded and submitted — the notebook itself and its
> description below are frozen and will not be revised, even where it no longer matches
> exactly what MP2 sections currently say. Treat 7.1 as a historical record, not a live
> tracking item.

### 7.1 Mini-project 1 EDA notebook
- [x] 🔴 `notebooks/01_weather_eda.ipynb`  (SUBSTANTIALLY BUILT — interpretation pending)
  - Loads weather data for all 3 regions from **CSV** (not SQLite)
  - Data-quality re-verification in-notebook (row counts, date range, 0 missing)
  - Three comparison axes: region vs region · time vs time · variable vs variable
  - **Three numbered questions up top**, answered by number in the conclusion
  - **Feature engineering:** growing degree days, water surplus (rain − ET0), rolling ET0
  - **Two-sample t-test** (Taranaki vs Auckland rainfall) — manual + scipy cross-check
  - Written output: plain-language findings paragraph (farmer language) + roadmap
  - ⚠ note: soil-moisture plot from v1.0 spec REMOVED (soil dropped from pull)
  - REMAINING: fill in per-chart `Finding` cells + conclusion blanks from rendered outputs
- [x] 🟡 `notebooks/02_market_price_eda.ipynb`  (RE-TAGGED MP2 lead-in — needs B+LNZ price data)
  - 10yr price series (lamb, mutton, steer); seasonal average by month (model baseline);
    peak months lamb vs beef; "best and worst months to sell" paragraph
- [x] 🟡 `notebooks/03_regional_comparison.ipynb`  (RE-TAGGED MP2 lead-in)
  - Climate profiles side by side; Stats NZ / B+LNZ stock numbers per region; region-selection
    justification with cited data

### 7.2 Mini-project 2 modelling notebooks
- [ ] 🟡 `notebooks/04_pasture_growth_model.ipynb`
  - Feature engineering (GDD, rainfall deficit/surplus, soil moving averages); XGBoost model;
    baseline (seasonal mean) comparison; feature importance per region
- [ ] 🟡 `notebooks/05_risk_classification.ipynb`
  - Drought/frost/flood classifier; precision/recall/confusion matrix; validate on known drought years
- [ ] 🟡 `notebooks/06_sell_signal_analysis.ipynb`
  - Combine pasture risk + price signal; 5-year backtest vs seasonal average

### 7.3 Mini-project 3 forecasting notebooks
- [ ] 🟡 `notebooks/07_price_forecasting.ipynb`
  - Prophet on B+LNZ price history; MAPE on hold-out; forecast vs actual (last 2 years)
- [ ] 🟡 `notebooks/08_combined_signal_test.ipynb`
  - End-to-end: weather → pasture risk → price forecast → plain-English output, per region;
    document wrong/uncertain cases
---

## SECTION 8 — STREAMLIT APPLICATION
*Lives in `/app/`. Farmer-facing. Simple. No jargon. (Streamlit provisional — tool decision deferred.)*

- [ ] 🟡 `app/app.py` — main entry point. Downgraded from 🔴: blocked behind Section 6.2
  models, which aren't built yet — nothing is actually stalled on this today.
- [ ] 🟡 `app/pages/01_farm_setup.py` — farm profile input. Same reasoning as above.
  - Region selector (3 large buttons); stock entry (ha / head count / stocking rate); silent LSU
    calculation; farm size category auto-assigned
- [ ] 🟡 `app/pages/02_dashboard.py` — main farmer view
  - Current conditions (rainfall last 7 days, temp); 7-day forecast (live Open-Meteo);
    current price vs seasonal average; pasture pressure LOW/NORMAL/HIGH
  - ⚠ "today's soil moisture" removed (no soil source yet)
- [ ] 🟡 `app/pages/03_pasture_risk.py` — 14-day risk GREEN/AMBER/RED; trigger; action; FEP line
- [ ] 🟡 `app/pages/04_market_signal.py` — price vs 3yr/5yr; direction forecast; SELL/BUY signals
- [ ] 🟡 `app/pages/05_recommendation.py` — 2-sentence plain-English daily summary
- [ ] 🟢 `app/components/ux_settings.py` — large-font default; high contrast; 6-hour offline cache
---

## SECTION 9 — CAPSTONE DOCUMENTATION
*Lives in `/docs/`. This is your portfolio. Every file should be something you're proud to show a client.*

- [ ] 🟢 `docs/methodology.md` — full scientific methodology (data sources + citations,
  model rationale, validation approach, known limitations, FEP context)
- [ ] 🟢 `docs/farmer_interview_notes.md` — Taranaki/Whanganui farmer notes, quotes
- [ ] 🟢 `docs/portfolio_narrative.md` — problem / what you built / what you learned / what it demonstrates
- [ ] 🟢 `docs/phase_summaries/phase1_summary.md`
- [ ] 🟢 `docs/phase_summaries/phase2_summary.md`
- [ ] 🟢 `docs/phase_summaries/phase3_summary.md`
- [ ] 🟢 Demo video (2 minutes) — region → stock → pasture + market + plain-English; host + README link
---

## SECTION 10 — FARMER VALIDATION
*The most important section. Cannot be downloaded. Must be earned.*

- [ ] 🟡 Farmer interview — Taranaki/Whanganui farmer
  - Three questions from the Research Brief; exact quotes (audio with permission ideal);
    permission to reference anonymously
- [ ] 🟢 Farmer feedback on MP1 dashboard — "useful? what's missing? what would you use?" → one paragraph
- [ ] 🟢 Farmer feedback on recommendation language — show 3 samples; "make sense? trust this?" → tune prompt
---

## QUICK REFERENCE — WHAT YOU NEED BY WHEN

| By | Must have | Status |
|----|-----------|--------|
| Week 1 setup | Repo, env, config, weather data (3 regions) | ✅ DONE |
| Reference data | LSU table (B+LNZ), regions.csv, farm classes | ✅ DONE (terrain_carrying_capacity.csv still to build) |
| Mini-project 1 (Jul 7) | Notebook 01 + 8-min presentation | ✅ DONE, submitted, frozen |
| Mini-project 2 (Sep 15) | Section 6.2, 6.5, Section 7.2, Section 8 pages 3–4 | started — Group A + C2 Signal 2 + recommendation stub done, Group B in progress |
| Mini-project 3 (Oct 1) | Section 6.3, Section 7.3, Section 8 page 5 | not started |
| Capstone (Oct 22) | Section 9 complete, Section 10 farmer quotes | not started |

---

## STILL-PENDING ITEMS (the open loops, in one place)
*Definitional/methodology decisions live once in FORMULAS.md's Open Decisions — not
duplicated here. This list is build-and-sequence items only.*

- B+LNZ citation permission for published reports (Stock Number Survey, Lamb Crop Report)
- Soil data source decision (Section 4.3 research)
- `terrain_carrying_capacity.csv` — still not built, genuinely blocking Group C2/E
- `minimum_residual_cover` per-terrain values — all four still `None` in config.py
  (separate from carrying-capacity SU/ha, which is resolved for all four terrain types —
  don't conflate the two tables)
- SU vs LSU basis confirmation before trusting `stocking_ratio` outputs
- Group E signal scaling and score→action thresholds — currently placeholder values in
  `recommendation_engine.py`, not tuned

---
*Checklist version 1.3 — July 2026. Full version history: `CHANGELOG.md`. Full
bibliography: `CITATIONS.md`. Full dataset register: `DATA_SOURCES.md`. Update this
document every time you add a new file or resolve a pending item — but log changes in
`CHANGELOG.md`, don't grow a change log inside this file again.*