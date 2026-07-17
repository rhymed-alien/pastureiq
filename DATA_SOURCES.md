# DATA_SOURCES.md — PastureIQ

Every dataset the project pulls, references, or plans to pull. Log a source here before
using it in code. Format: **Full name | URL/source | Licence | Access date | Variables
used | Decision supported**.

Status key: **LIVE** = pulled and in the repo · **VERIFIED** = source confirmed
accessible, not yet pulled · **PENDING** = requested, awaiting reply · **PLANNED** =
identified, not yet requested · **DEAD END** = investigated, not usable.

---

## Weather

**Open-Meteo Historical Weather API (ERA5 Archive)**
- URL: https://archive-api.open-meteo.com/v1/archive
- Licence: free API tier = non-commercial use only; underlying data CC BY 4.0
  (attribution required — text saved to `docs/licensing/openmeteo_attribution.txt`)
- Access: pulled via `src/pull_weather.py`, all 3 regions, 2015–2026, daily
- Variables used: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`,
  `et0_fao_evapotranspiration`, `windspeed_10m_max`
  - ⚠ Soil variables (`soil_moisture_0_to_7cm`, `soil_temperature_0cm`) removed — caused a
    400 error on this endpoint (hourly-only/inconsistent on ERA5 archive). Soil sourcing
    is a separate open research task, not part of this pull.
- Decision supported: Group B pasture growth model (temperature, rainfall, water surplus
  = rainfall − ET0); Group F confidence model context
- Status: **LIVE** — `weather_waikato.csv`/`.json`, `weather_taranaki.csv`/`.json`,
  `weather_auckland.csv`/`.json`, 4177 rows each, 0 missing, verified.

**Open-Meteo Forecast API**
- URL: same base API, forecast endpoint (not yet called)
- Decision supported: live 7-day forecast for the dashboard, Group F short-horizon input
- Status: **PLANNED** — `get_forecast_weather()` not yet added to `pull_weather.py`; no
  consumer until the dashboard is built (MP2).

**NIWA seasonal climate outlooks**
- URL: https://niwa.co.nz/climate-and-weather/seasonal-climate-outlooks
- Licence: unconfirmed — written reply pending
- Decision supported: contextual background for market timing (not used in calculations)
- Status: **PENDING** — email sent to data@niwa.co.nz, capstone/non-commercial/portfolio
  use requested, follow-up scheduled. Do not use until licence confirmation received and
  saved to `docs/licensing/niwa_licence_confirmation.pdf`.

---

## Stock Units / Livestock Reference

**B+LNZ Sheep & Beef Farm Survey — Stock Unit Conversions**
- Source: supplied directly by B+LNZ Economic Service via email, 2026-06-24
- Licence: supplied specifically for this free, non-commercial student project; crediting
  acknowledged. Citation permission for *published reports* is separate — see below.
- Variables used: animal_class, category, stock_units, cattle_equivalent, source_note
  (use `stock_units` column for feed maths — NOT `cattle_equivalent`)
- Decision supported: Group A feed demand (`total_LSU`, `daily_feed_demand_kgDM`)
- Status: **LIVE** — `lsu_conversion_table.csv` built 2026-06-24. Provenance in
  `docs/blnz_lsu_source_record.md` (verbatim email + table).
- Caveat (per B+LNZ): general guide for policy-level implied feed utilisation, not a
  substitute for farm-level feed budgeting. Figures held constant for years by B+LNZ to
  preserve a consistent timeseries — currently under review on their side.

**B+LNZ Farm Class Benchmarks (carrying capacity ranges)**
- URL: https://beeflambnz.com/industry-data/farm-data-and-industry-production/farm-classes
- Variables used: terrain_type, min_su_per_ha, max_su_per_ha
- Verified ranges: hard hill 2–7 SU/ha · steep hill 6–10 · easier hill 7–13 · high country
  ≤3 · lifestyle_flat 4.5–15.5 (sourced separately, see Auckland Council TR2017/020 below)
- Decision supported: `terrain_carrying_capacity.csv`, Group C2 Signal 2 stocking ratio
  ceiling
- Status: **VERIFIED** (ranges confirmed) / **partially LIVE** — hard hill/steep
  hill/easier hill/high country sourced from B+LNZ directly; `lifestyle_flat` sourced from
  a different dataset (TR2017/020) since B+LNZ's farm classes don't cover lifestyle blocks.
  `terrain_carrying_capacity.csv` file itself still needs building.

**B+LNZ Fact Sheet 90 (FS90) / Fact Sheet 83 (FS83)**
- Decision supported: cattle LSU derivation; terrain feed-cost uplift figures (hard hill
  cow ~65 MJME/day vs ~55 easy hill; +0.5 MJME steep sheep) — not yet quantified into code
- Status: **CITED**, not pulled as a structured dataset. See CITATIONS.md.

---

## Pasture Growth

**Cichota et al. (2014) — APSIM sheep/beef simulation (Waikato)**
- Decision supported: Waikato pasture growth curve annual magnitude (8493 kg DM/ha/yr,
  LUC Class 6 steep hill)
- Status: **LIVE** — figure applied in `pasture_growth_curve.csv`, scale factor 0.4819.

**Auckland Council TR2017/020 (Hicks & Curran-Cournane, 2017), Appendix 2**
- Decision supported: West Auckland pasture growth curve annual magnitude (6900 kg
  DM/ha/yr) and `lifestyle_flat` carrying capacity (4.5–15.5 SU/ha)
- Status: **LIVE** — both figures applied.

**DairyNZ Ruakura/Newstead (1996–2017 avg)**
- Decision supported: monthly *shape* (not magnitude) for Waikato and West Auckland
  pasture growth curves — a dairy-farm proxy, explicitly flagged as unresolved
- Status: **LIVE**, flagged as proxy — revisit if sheep/beef monthly-resolution data is
  ever found.

**DairyNZ Hawera WTARS**
- Decision supported: Taranaki pasture growth curve, both shape and magnitude
- Status: **LIVE**, flagged as full proxy — no sheep/beef-specific Taranaki source found.

**Taranaki DTT Stratford**
- Decision supported: candidate for a genuinely trained (non-proxy) Taranaki model
- Status: **PLANNED** — flagged in appendix, MP3 candidate, not yet investigated.

---

## Market Price

**B+LNZ Farmgate Price Trends**
- Source: supplied directly by B+LNZ Economic Service (same direct-request channel as the
  LSU conversion table) — RESOLVED, not the public price-trend-graphs page.
- Licence: supplied specifically for this free, non-commercial student project, same terms
  as the LSU data. Citation permission for B+LNZ's *published reports* (Stock Number
  Survey, Lamb Crop Report) remains separate and still pending — do not conflate the two.
- Variables: date (monthly), species, class, price_nzd_per_kg
- Species/classes: lamb (YM lamb, all-grades), mutton, beef (steer, heifer, cow, bull)
- Decision supported: Group D market signal (`price_vs_seasonal`), Group E scoring
- Status: **LIVE** — `blnz_farmgate_prices.csv` delivered as an MP1 output. Row
  counts/date range/missing-value verification done in
  `01_weather_and_market_eda.ipynb`.

**MPI Slaughter Statistics**
- URL: https://www.mpi.govt.nz/resources-and-forms/economic-intelligence/data
- Format: monthly, XLSX, updated 25th of each month (1-month lag)
- Decision supported: seasonal supply signal for market timing, correlation check against
  B+LNZ price data
- Status: **VERIFIED** live 2026-06-24, not yet pulled.

**MPI SOPI Data** (Situation & Outlook for Primary Industries)
- Format: XLSX, ~65 KB, export volumes/prices/revenue, historical + forecast
- Decision supported: cross-validation for price signals
- Status: **VERIFIED** live 2026-06-24, not yet pulled.

**Stats NZ — Livestock Slaughtering Statistics (Infoshare)**
- URL: stats.govt.nz → "Livestock slaughtering statistics" → "Access data in Infoshare"
- Format: downloadable time-series, region × animal type, monthly
- Decision supported: long regional supply time-series, validates B+LNZ price seasonality
- Status: **VERIFIED** live, not yet pulled.

**B+LNZ Stock Number Survey (30 June 2025)**
- Format: PDF, held/uploaded
- Decision supported: regional stock-number tables (Northland–Waikato–BoP,
  Taranaki–Manawatū coarse regions); citable anchor for pastoral grazing ≈ 85% of
  sheep & beef farm area, supporting `effective_hectares` definition
- Licence: "no reproduction without permission" — cite with attribution
- Status: **HELD**, citation permission pending confirmation from B+LNZ.

**B+LNZ Lamb Crop Report 2025**
- Same licence caveat and status as Stock Number Survey above.
- Decision supported: regional feed commentary, lamb crop and ewe performance context.

**USDA GAIN Reports — NZ Livestock (2025/2026)**
- URL: https://apps.fas.usda.gov (search: New Zealand Livestock Products)
- Decision supported: export market context, optional validation
- Status: **PLANNED**, not yet requested/pulled.

---

## Census / Population

**Stats NZ Agricultural Production Census 2022**
- URL: https://www.stats.govt.nz/information-releases/agricultural-production-statistics-year-to-june-2022-final/
- Decision supported: farm count and livestock numbers per region, documentation context
- Status: **PLANNED**, not yet pulled.

**MPI Lifestyle Block Analysis 2024** (Technical Paper 2024/03)
- URL: https://www.mpi.govt.nz/dmsdocument/61048-Lifestyle-block-analysis
- Decision supported: justification for lifestyle block farm size definitions (5–20ha)
- Status: **PLANNED**, not yet pulled.

---

## Dead Ends (do not re-chase)

**NZ Meat Board slaughter page** — redirects to B+LNZ, not an independent source. **DEAD
END**, logged 2026-06-24.

**Rabobank agri reports** — PDF-only commentary, no raw/machine-readable data. **DEAD
END**, logged 2026-06-24.

---
*Data sources register v1.0 — rebuilt from PROJECT_SPEC.md, MRS.md Sections 2–5, and
FORMULAS.md source notes. Log every new dataset here before it's used in code, per the
existing MRS rule.*