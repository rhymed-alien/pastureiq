# MASTER REFERENCE CHECKLIST
## PastureIQ — NZ Farm Pasture & Market Decision Tool
**Version:** 1.2 | **Date:** July 2026 | **Deadline:** October 22 2026
 
> **v1.2 update:** reconciled against the B+LNZ data reply (2026-06-24) and MP1 build progress.
> Key changes: LSU conversion table built and sourced (beef cow now 5.5, national/feed-only);
> weather EDA notebook substantially built (loads CSV, not SQLite); alternative livestock data
> sources verified; MP1 scope clarified to notebook 01 only. See CHANGE LOG at foot of document.
>
> **v1.1 reconciliation (retained):** cross-checked against PROJECT_SPEC.md and FORMULAS.md.
> Where this checklist and PROJECT_SPEC disagree, PROJECT_SPEC is the authority on
> goal/IO/formulas; this checklist is the authority on files-to-build and sequence.
 
---
 
## HOW TO USE THIS DOCUMENT
 
- Work through each section in order
- Tick items off as you acquire or create them
- Items marked 🔴 are blockers — nothing downstream works without them
- Items marked 🟡 are needed before a specific mini-project
- Items marked 🟢 are nice-to-have or capstone polish items
- Every data file needs a corresponding entry in DATA_SOURCES.md before you use it
- `[x]` = done & verified · `[ ]` = not yet · `[~]` = partially done / pending an external reply
---
 
## SECTION 1 — PROJECT INFRASTRUCTURE
*Set up once, never redo. All of this belongs in Week 1.*
 
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
- [~] 🔴 NIWA written reply saved to `/docs/licensing/niwa_licence_confirmation.pdf` (PENDING — awaiting reply)
- [x] 🔴 Open-Meteo attribution text saved to `/docs/licensing/openmeteo_attribution.txt`
  - Text required: "Weather data from Open-Meteo.com (CC BY 4.0)"
  - NOTE: free Open-Meteo API = non-commercial use only; the DATA is CC BY 4.0. Record both.
- [~] 🟡 B+LNZ terms / use permission — B+LNZ Economic Service supplied LSU data directly for this
  free non-commercial student project (2026-06-24) and is crediting acknowledged. Still to do:
  save a short note confirming citation permission for their published reports (Stock Number
  Survey, Lamb Crop Report) to `/docs/licensing/blnz_terms.txt`.
- [ ] 🟡 Stats NZ Crown copyright acknowledgement saved to `/docs/licensing/statsnz_crown_copyright.txt`
### 1.3 Core documentation files
- [~] 🔴 `DATA_SOURCES.md` — log every source before you use it
  - Logged: Open-Meteo (weather); B+LNZ Stock Unit Conversions (LSU)
  - Placeholder added: B+LNZ Farmgate Price Trends (pending — see 4.1)
  - Format: Full name | URL/source | Licence | Access date | Variables used | Decision supported
- [~] 🔴 `FARMER_DECISIONS.md` — the 5 decisions the app must support (STARTED: stub created)
- [x] 🔴 `docs/PROJECT_SPEC.md` — goal, inputs, outputs, scope, infrastructure, build status
- [x] 🔴 `docs/FORMULAS.md` — complete formula reference, Groups A–G incl. bias correction
  - v1.1: LSU pending-flags closed (Open Decisions #3 resolved, #4 partial — lamb feed-side)
- [x] 🔴 `docs/blnz_lsu_source_record.md` — verbatim B+LNZ email + LSU table + provenance (NEW)
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
  - **BUILT 2026-06-24 from B+LNZ Sheep & Beef Farm Survey standard conversions** (supplied by
    B+LNZ Economic Service by email). Provenance: `docs/blnz_lsu_source_record.md`.
  - **Baseline:** 1 LSU = 6000 MJME/year = 520 kg DM/year (modern NZ standard ewe). Confirmed as
    the ewe = 1.0 definitional unit. Source: RuralHQ (2019); Otago RC memo (2023) citing Parker (1998).
  - **Columns:** animal_class, category, stock_units, cattle_equivalent, source_note
  - **⚠ USE THE `stock_units` COLUMN for feed maths** — NOT `cattle_equivalent` (a within-cattle
    relative ratio, not a feed figure).
  - **Values (B+LNZ survey standard):**
    - Sheep: ewe 1.0 · hogget 0.7 · wether 0.7 · ram 0.8 · grazing sheep 0.7 (from 2009-10 Survey)
    - Beef: M.A. cow 5.5 · heifer 2.5yr 5.5 · heifer 1.5yr 4.5 · heifer weaner 3.5 · bull weaner 4.5 ·
      steer weaner 4.5 · steer 1.5yr 5.0 · steer 2.5yr 5.5 · bull beef 1.5yr+ 5.5 · bull breeding 5.5
    - Dairy grazers: R1 heifer 3.5 · R2 heifer 4.5 · dairy cow (winter) 1.1
  - **⚠ RESOLVED — beef cow now 5.5:** B+LNZ survey value supersedes BOTH the earlier project
    estimate (5.8) AND RuralFind (4.4). The earlier 5.8 folded hard-hill-country terrain effect
    into the LSU value; that terrain adjustment now lives in the carrying-capacity modifier
    (Section 2.1 terrain file / FORMULAS.md Group B), keeping LSU national and feed-only per design.
  - **⚠ PARTIAL — lamb feed-side value:** B+LNZ table has no standalone "lamb"; nearest survey
    class is grazing sheep (0.7). Confirm treatment when Group A / stock_units.py is coded.
  - **Caveat (per B+LNZ):** these are a general guide for policy-level implied feed utilisation,
    NOT a substitute for farm-level feed budgeting. Figures are currently UNDER REVIEW by B+LNZ
    (held constant for years to preserve a consistent timeseries).
  - **NOTE:** deer OUT of scope (not in target regions' primary stock profile).
- [ ] 🔴 `terrain_carrying_capacity.csv` — NZ carrying capacity by terrain type (THIS is where terrain lives)
  - **Source:** B+LNZ farm class benchmarks (verified ranges)
  - **URL:** https://beeflambnz.com/industry-data/farm-data-and-industry-production/farm-classes
  - **Columns needed:** terrain_type, min_su_per_ha, max_su_per_ha, notes
  - **Verified values:** hard hill (2–7 SU/ha), steep hill (6–10), easier hill (7–13), high country (≤3)
  - **NOTE:** hard-hill-country terrain modifier (previously baked into beef cow 5.8) belongs here /
    in the Group B growth model, not in LSU.
### 2.2 Region reference data
- [x] 🔴 `regions.csv` — your three target regions (REFERENCE/documentation layer)
  - **NOTE on source of truth:** config.py holds the region coords the CODE runs on. regions.csv is
    the richer REFERENCE file (rainfall, sunshine, farm class). config.py wins if they ever differ.
  - **Columns:** region_id, name, label, lat, lon, terrain_type, avg_annual_rainfall_mm,
    avg_sunshine_hours, blnz_farm_class, notes
  - **Region 1:** South Waikato / King Country — lat: -38.34, lon: 175.16 (Te Kūiti area)
  - **Region 2:** South Taranaki / N. Whanganui hill country — lat: -39.63, lon: 174.93
  - **Region 3:** West Auckland lifestyle blocks — lat: -36.90, lon: 174.52
- [x] 🟡 `blnz_farm_classes.csv` — B+LNZ farm class reference table
  - **Source:** B+LNZ farm class descriptions
  - **URL:** https://beeflambnz.com/industry-data/farm-data-and-industry-production/farm-classes
  - **Columns:** class_id, name, su_per_ha_min, su_per_ha_max, terrain_description, typical_ha_range
### 2.3 Scientific citations register
- [ ] 🔴 `citations.bib` OR `CITATIONS.md` — every paper and report cited in the project
  - Prof. Coop (1965) — standard ewe definition, LSU system basis
  - Parker, P. (1998) — Standardisation between livestock classes: use and misuse of the stock unit system
  - Taylor & Letham (2018) — Forecasting at Scale (Facebook Prophet) — https://doi.org/10.1080/00031305.2017.1380080
  - Woodward et al. — NZ Journal of Agricultural Research — weather-driven pasture growth models
  - Amies et al. (2021) — National Mapping of NZ Pasture Productivity Using Temporal Sentinel-2 Data — https://doi.org/10.3390/rs13081481
  - Zippenfenig, P. (2023) — Open-Meteo.com Weather API — https://doi.org/10.5281/zenodo.7970649
  - Rural Leaders NZ (2019) — Technology use by sheep and beef farmers
  - Rural Leaders NZ (2025) — Technology adoption on NZ sheep and beef farms (Campbell-Smith)
  - B+LNZ Sheep & Beef Farm Survey — stock unit conversions (LSU source, 2026)
  - B+LNZ Stock Number Survey (as at 30 June 2025) — national/regional stock numbers
  - B+LNZ Lamb Crop Report 2025 — lamb crop, ewe performance, regional feed commentary
  - B+LNZ New Season Outlook 2024–25
  - B+LNZ Farm Facts 2023
  - Taranaki Regional Council State of Environment 2022
  - Stats NZ Agricultural Production Census 2022
  - Treasury NZ FEU Special Topic — NZ Meat Exports (2025)
---
 
## SECTION 3 — WEATHER DATA
*Dynamic. Pulled via API. Stored in `/data/raw/weather/`*
 
### 3.1 Historical weather — Open-Meteo ERA5  [DONE & VERIFIED]
- [x] 🔴 `weather_waikato.csv` + `.json` — South Waikato 2015–2026 (4177 rows, 0 missing)
- [x] 🔴 `weather_taranaki.csv` + `.json` — South Taranaki 2015–2026 (4177 rows, 0 missing)
- [x] 🔴 `weather_auckland.csv` + `.json` — West Auckland 2015–2026 (4177 rows, 0 missing)
  - **API:** https://archive-api.open-meteo.com/v1/archive
  - **Variables pulled (daily) — soil REMOVED, see note:**
    - `temperature_2m_max` · `temperature_2m_min` · `precipitation_sum` ·
      `et0_fao_evapotranspiration` · `windspeed_10m_max`
  - **⚠ SOIL VARIABLES REMOVED:** soil_moisture_0_to_7cm and soil_temperature_0cm caused a 400
    error (hourly-only / inconsistent on the ERA5 archive). Soil sourcing is now a RESEARCH task
    (Section 4.3), not part of this pull.
  - **Format:** daily; both raw JSON (provenance) and CSV (working) saved per region
  - **Licence:** free Open-Meteo API = non-commercial use only; DATA licensed CC BY 4.0 (attribution required)
  - **Pulled via:** `src/pull_weather.py` (loops all regions from config.py), run `python -m src.pull_weather`
  - **NOTE:** the MP1 notebook loads these CSVs DIRECTLY (no SQLite yet — database.py deferred).
### 3.2 Weather forecast — Open-Meteo live
- [ ] 🔴 `get_forecast_weather()` in `src/pull_weather.py` — calls Open-Meteo forecast API
  - Returns: 7-day daily forecast for any lat/lon; same variables as historical pull
  - Called live in the dashboard on page load (dashboard = Streamlit, provisional; decision deferred)
  - **NOTE:** deferred — no consumer until the dashboard is built (MP2). Not needed for MP1.
### 3.3 Seasonal climate outlooks — NIWA (subject to licence confirmation)
- [ ] 🟡 NIWA seasonal outlook PDFs for target regions — download quarterly
  - **URL:** https://niwa.co.nz/climate-and-weather/seasonal-climate-outlooks
  - **Use:** Contextual background for market timing module — not used in model calculations
  - **Condition:** Only if NIWA written licence confirms non-commercial portfolio use is permitted
---
 
## SECTION 4 — MARKET PRICE DATA
*Semi-static. Download monthly. Lives in `/data/raw/market/`*
 
### 4.1 B+LNZ farmgate prices — primary market dataset
- [~] 🔴 `blnz_farmgate_prices_raw.csv` — all species, all years available
  - **STATUS (2026-06-24):** requested from B+LNZ Economic Service; reply received confirming they
    WILL supply price trend data — in progress on their side, awaited. Log access date + coverage
    in DATA_SOURCES.md on receipt; verify row counts / date range / missing values after the pull.
  - **URL (public graphs):** https://beeflambnz.com/industry-data/farm-data-and-industry-production/price-trend-graphs
  - **Columns needed:** date (monthly), species, class, price_nzd_per_kg
  - **Species/classes to include:**
    - Lamb: YM lamb, all-grades lamb
    - Sheep: mutton
    - Beef: steer, heifer, cow, bull
### 4.2 MPI slaughter statistics
- [ ] 🟡 `mpi_slaughter_stats_raw.xlsx` — monthly livestock slaughter, all species
  - **URL:** https://www.mpi.govt.nz/resources-and-forms/economic-intelligence/data
  - **Updated:** 25th of each month (1-month lag)
  - **Use:** Seasonal supply signal for market timing module
  - **VERIFIED LIVE 2026-06-24:** page hosts "Livestock slaughter statistics … [XLSX]" and a
    separate "SOPI data [XLSX]" (situation & outlook — export volumes/prices/revenue). Both free.
### 4.3 Soil data — RESEARCH TASK (parked after Open-Meteo soil proved unreliable)
- [ ] 🟡 Research + compare trustworthy NZ soil moisture / soil temperature sources before
      building soil into the model. Candidates to verify (access, licence, resolution, history):
  - Open-Meteo ERA5-Land hourly soil vars (aggregate hourly→daily yourself)
  - Open-Meteo Historical Forecast API (better soil, but only ~2021 onward)
  - NIWA soil moisture stations (pending licensing reply)
  - Manaaki Whenua / Landcare S-map (NZ soil database — static properties vs time-series?)
  - Regional council / LINZ open data portals
  - **DECISION to record:** which soil source (if any) enters the model, or proxy soil from
    rainfall + ET0 instead. Log findings in DATA_SOURCES.md. Research-and-decide, NOT build.
### 4.4 Alternative NZ livestock data — VERIFIED (NEW, 2026-06-24)
*Independent, machine-readable supply-side sources outside B+LNZ, plus B+LNZ context reports.*
- [ ] 🟡 Stats NZ — Livestock Slaughtering Statistics (via Infoshare)
  - **URL:** stats.govt.nz → "Livestock slaughtering statistics" → "Access data in Infoshare"
  - **Group:** Livestock slaughtering – LSS. Downloadable time-series (region × animal type), monthly.
  - **Use:** long regional supply time-series; validates B+LNZ price seasonality.
- [ ] 🟡 MPI — SOPI data (XLSX, ~65 KB) — export volumes/prices/revenue, historical + forecast
  - **Use:** cross-validation for price signals (Section 4.1).
- [~] 🟢 B+LNZ Stock Number Survey (30 June 2025) + Lamb Crop Report 2025 — HELD (PDFs uploaded)
  - **Use:** regional stock-number tables (2023/24/25) — Northland-Waikato-BoP and Taranaki-Manawatū
    map to two of the three target regions (coarse regions — context, not farm-level).
  - **Citable anchor:** pastoral grazing ≈ 85% of sheep & beef farm area (⇒ ~15% non-grazeable) —
    supports the `effective_hectares = total − non_grazeable` definition (FORMULAS.md Group B).
  - **⚠ copyright:** reports carry "no reproduction without permission" — cite figures with
    attribution; confirm citation permission via B+LNZ contact (see 1.2).
- [x] 🟢 DEAD-ENDS logged (do not re-chase): NZ Meat Board slaughter page redirects to B+LNZ (not
  independent); Rabobank agri reports are PDF-only commentary (no raw data).
### 4.5 USDA GAIN reports — NZ livestock (optional validation)
- [ ] 🟢 `usda_gain_nz_livestock_2025.pdf` and `2026.pdf`
  - **URL:** https://apps.fas.usda.gov (search: New Zealand Livestock Products)
  - **Use:** Export market context — cross-validates B+LNZ price signals with global demand view
---
 
## SECTION 5 — FARM POPULATION & CENSUS DATA
*Static. Download once. Lives in `/data/raw/census/`*
 
- [ ] 🟡 `statsnz_agcensus_2022_regional.xlsx` — agricultural census results by region
  - **URL:** https://www.stats.govt.nz/information-releases/agricultural-production-statistics-year-to-june-2022-final/
  - **Use:** Farm count and livestock numbers per region — context for documentation
  - **Columns needed:** region, farm_type, number_of_farms, livestock_numbers_by_class
- [ ] 🟡 `statsnz_livestock_slaughter_timeseries.xlsx` — historical slaughter time series
  - **URL:** https://www.stats.govt.nz/topics/agriculture/ (see also Section 4.4 Infoshare route)
  - **Use:** Long-run seasonal patterns to validate B+LNZ price seasonality
- [ ] 🟢 `mpi_lifestyle_block_analysis_2024.pdf` — MPI Technical Paper 2024/03
  - **URL:** https://www.mpi.govt.nz/dmsdocument/61048-Lifestyle-block-analysis
  - **Use:** Justification for lifestyle block farm size definitions (5–20ha)
---
 
## SECTION 6 — PYTHON SOURCE FILES
*Lives in `/src/`. Each file is a standalone module with a docstring citing its data sources.*
 
### 6.1 Core modules — Mini-project 1
- [x] 🔴 `src/stock_units.py`  (FEED-ONLY — terrain does NOT belong here)
  - `LSU_VALUES` dictionary — now populated from `lsu_conversion_table.csv` (Section 2.1, B+LNZ)
  - `calculate_total_lsu(stock_dict)` — sums class_count × class_LSU
  - `daily_feed_demand_kgDM(total_lsu)` — total_lsu × 1.42 (520 kg DM/yr ÷ 365; annual avg)
  - ⚠ terrain NOT here — lives in carrying capacity (regions.csv / Section 2.1). Pasture pressure is
    computed in the balance step (FORMULAS.md Group C).
  - ⚠ decide lamb feed-side treatment (grazing sheep 0.7?) when coding — see 2.1 partial gap.
  - Docstring: cite B+LNZ Sheep & Beef Farm Survey conversions, Coop (1965), Parker (1998), FS90/FS83
- [~] 🔴 `src/pull_weather.py`  (DONE for historical)
  - Open-Meteo archive call, loops all regions, saves JSON+CSV
  - STILL TO ADD: `get_forecast_weather(lat, lon)` — 7-day forecast (deferred to dashboard/MP2)
  - Docstring: cite Open-Meteo / Zippenfenig (2023)
- [ ] 🟡 `src/database.py`  (DEFERRED — MP1 runs on CSV, not SQLite)
  - `create_schema()` · `load_weather(df, region_id)` · `load_prices(df)` ·
    `query_weather_summary(...)` · `query_price_trend(...)`
  - **NOTE:** re-tagged 🟡 — not required for MP1 (notebook loads CSVs directly). Build when the
    dashboard or price data needs a query layer.
- [x] 🔴 ~~`src/regions.py`~~ — SUPERSEDED. config.py holds the REGIONS dict + coords as the code
  source of truth. regions.csv = reference layer only.
### 6.2 Analysis modules — Mini-project 2
- [ ] 🟡 `src/pasture_model.py`
  - `estimate_pasture_growth_rate(temp, rainfall, soil_moisture, et0)` — weather to kg DM/ha/day
  - `calculate_days_of_feed(total_lsu, farm_ha, growth_rate)` — forward pasture cover estimate
  - `classify_pasture_risk(days_of_feed, season)` — returns GREEN / AMBER / RED
  - Docstring: cite Woodward et al. NZ Journal of Agricultural Research
- [ ] 🟡 `src/market_model.py`
  - `get_seasonal_average(species, month)` — returns 5yr average price for that month
  - `classify_price_signal(current_price, seasonal_avg)` — HIGH / AVERAGE / LOW
  - `generate_sell_signal(pasture_risk, price_signal, stock_type)` — BUY / HOLD / SELL
### 6.3 Forecasting modules — Mini-project 3
- [ ] 🟡 `src/price_forecast.py`
  - Prophet model for farmgate price direction
  - `train_prophet_model(price_df, species)` · `forecast_price_direction(model, weeks_ahead)` → UP/FLAT/DOWN + confidence
  - Docstring: cite Taylor & Letham (2018)
- [ ] 🟡 `src/plain_english.py`
  - `generate_recommendation(pasture_risk, price_signal, price_forecast, farm_profile)`
  - Calls Anthropic API (claude-sonnet) with model outputs as structured input
  - Returns 2-sentence plain-English recommendation; short, no jargon, honest about uncertainty
### 6.4 Utility modules
- [ ] 🟡 `src/data_loader.py`
  - Load and clean each raw data file; standardise date formats, column names, units
  - Log anomalies to data_quality.md
- [ ] 🟢 `src/fep_alerts.py`
  - Regional rainfall threshold alert for papa soil (Taranaki), hard-coded from TRC guidance
### 6.5 Prediction logging & confidence (infrastructure for cross-check + learning)
*Build the LOG structure early even if the models that fill it come in MP2/MP3. See
FORMULAS.md Groups F (confidence) and G (bias correction).*
- [x] 🟡 `data/predictions/predictions_log.csv` — schema:
  `date_made, region, horizon_days, variable, predicted_value, confidence, target_date, actual_value, error`
- [x] 🟡 `src/predictions_log.py`
  - `log_prediction(...)` · `mature_predictions()` · `compute_bias(region, variable, horizon)` ·
    `apply_bias_correction(raw_prediction, bias)` (corrected = raw − bias)
- [x] 🟡 Confidence model (config.py + applied in recommendation logic):
  - 7 / 14 / 28 days → HIGH (~0.85) / MEDIUM (~0.60) / LOW-OUTLOOK (~0.40)
  - Sources: AMS; JGU/Riemer; Weather Company; S2S hydropower study
  - DESIGN RULE: 4-week output framed as TREND/OUTLOOK, never a daily forecast.
---
 
## SECTION 7 — NOTEBOOKS
*Lives in `/notebooks/`. Every notebook has a markdown cell at the top explaining its purpose in plain language.*
 
> **MP1 scope clarification (v1.2):** MP1 deliverable = notebook 01 (weather EDA) + the 8-min
> presentation. Notebooks 02 (market price) and 03 (regional comparison) are RE-TAGGED as MP2
> lead-in / if-time-permits — they depend on price data and deeper analysis not needed for the
> July 7 graded deliverable. This matches the "Option A" scoping decision.
 
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
 
- [ ] 🔴 `app/app.py` — main entry point
- [ ] 🔴 `app/pages/01_farm_setup.py` — farm profile input
  - Region selector (3 large buttons); stock entry (ha / head count / stocking rate); silent LSU
    calculation; farm size category auto-assigned
- [ ] 🔴 `app/pages/02_dashboard.py` — main farmer view (MP1-era feature, built in MP2 app phase)
  - Current conditions (rainfall last 7 days, temp); 7-day forecast (live Open-Meteo);
    current price vs seasonal average; pasture pressure LOW/NORMAL/HIGH
  - ⚠ "today's soil moisture" from v1.0 spec removed (no soil source yet)
- [ ] 🟡 `app/pages/03_pasture_risk.py` — 14-day risk GREEN/AMBER/RED; trigger; action; FEP line
- [ ] 🟡 `app/pages/04_market_signal.py` — price vs 3yr/5yr; direction forecast; SELL/BUY signals
- [ ] 🟡 `app/pages/05_recommendation.py` — 2-sentence plain-English daily summary
- [ ] 🟢 `app/components/ux_settings.py` — large-font default; high contrast; 6-hour offline cache
---
 
## SECTION 9 — CAPSTONE DOCUMENTATION
*Lives in `/docs/`. This is your portfolio. Every file should be something you're proud to show a client.*
 
- [ ] 🟢 `docs/methodology.md` — full scientific methodology
  - Data sources + citations; model rationale (why XGBoost, why Prophet); validation approach;
    known limitations (ERA5 resolution in steep terrain, papa soil caveat); FEP context
- [ ] 🟢 `docs/farmer_interview_notes.md` — Taranaki/Whanganui farmer notes, quotes (with permission),
  how feedback shaped design
- [ ] 🟢 `docs/portfolio_narrative.md` — problem / what you built / what you learned / what it demonstrates
- [ ] 🟢 `docs/phase_summaries/phase1_summary.md`
- [ ] 🟢 `docs/phase_summaries/phase2_summary.md`
- [ ] 🟢 `docs/phase_summaries/phase3_summary.md`
- [ ] 🟢 Demo video (2 minutes) — region → stock → pasture + market + plain-English; host + README link
---
 
## SECTION 10 — FARMER VALIDATION
*The most important section. Cannot be downloaded. Must be earned.*
 
- [ ] 🟡 Farmer interview — Taranaki/Whanganui farmer (end of June 2026)
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
| Mini-project 1 (Jul 7) | Notebook 01 + 8-min presentation | DONE
| Mini-project 2 (Sep 15) | Section 6.2, 6.5, Section 7.2, Section 8 pages 3–4 | started |
| Mini-project 3 (Oct 1) | Section 6.3, Section 7.3, Section 8 page 5 | Not started |
| Capstone (Oct 22) | Section 9 complete, Section 10 farmer quotes | Not started |
 
---
 
## STILL-PENDING ITEMS (the open loops, in one place)
- B+LNZ citation permission for published reports (Stock Number Survey, Lamb Crop Report)
- Soil data source decision (Section 4.3 research)
- Pasture-cover input method: farmer-entered vs tool-estimated (FORMULAS.md Group C)
- minimum_residual_cover exact NZ figure (FORMULAS.md Group C)
- Lamb feed-side LSU treatment (grazing sheep 0.7 nearest; confirm when coding Group A) confirmed
- SU vs LSU basis confirmation before C2 stocking_ratio (should be same ewe-equivalent)
## RESOLVED THIS CYCLE (moved off the pending list)
- ✅ Per-class LSU conversion table — supplied by B+LNZ, built (Section 2.1)
- ✅ beef cow LSU — resolved to 5.5 (B+LNZ survey); terrain effect moved to carrying-capacity modifier
- ✅ hogget / ram / wether / grazing-sheep / full cattle LSU values — supplied by B+LNZ
- ✅ Alternative livestock data sources — verified (Stats NZ Infoshare, MPI SOPI); dead-ends logged
---
 
*Checklist version 1.2 — July 2026*
*Cross-checked against PROJECT_SPEC.md and FORMULAS.md; reconciled with B+LNZ data reply (2026-06-24)*
*Update this document every time you add a new file, data source, or resolve a pending item*
 
## CHANGE LOG (v1.1 → v1.2)
- Section 2.1: LSU table built from B+LNZ; beef cow 5.8→5.5 (national/feed-only; terrain→modifier);
  hogget 1.0→0.7; full sheep+cattle+dairy classes added; 4.4-vs-5.8 discrepancy resolved.
- Section 1.3: added blnz_lsu_source_record.md; DATA_SOURCES.md now logs B+LNZ LSU + price placeholder.
- Section 3.1: noted MP1 loads CSV directly (not SQLite).
- Section 4.1: B+LNZ prices — reply received, data in progress.
- Section 4.2 / 4.4: verified MPI SOPI + Stats NZ Infoshare live; added B+LNZ reports; logged dead-ends.
- Section 6.1: stock_units.py LSU now sourced; database.py re-tagged 🟡 (deferred, CSV for MP1).
- Section 7.1: notebook 01 status [~], content corrected (soil removed; questions + features + t-test
  added); notebooks 02/03 re-tagged as MP2 lead-in (MP1 scope = notebook 01 only).
- Section 8: removed soil-moisture references from dashboard spec.