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

**⚠ FABRICATION FLAG (found and corrected 2026-07-17):** the two entries previously here,
"DairyNZ Ruakura/Newstead (1996–2017 avg)" and "DairyNZ Hawera WTARS," did not exist. No
such documents are held anywhere in this project. A past session invented them, including
a false "cross-confirmed against DairyNZ Facts and Figures PDF" claim for the Taranaki
values. Both entries are removed below and replaced with what's real. If
`pasture_growth_curve.csv` in the repo still cites either name, it needs rebuilding — see
FORMULAS.md Group B.

**Cichota et al. (2014) — APSIM sheep/beef simulation (Waikato/Canterbury/Southland)**
- Full citation: `CITATIONS.md`
- Source file (transcribed & verified against PDF 2026-07-17):
  `data/raw/reference/pasture_growth_sources/cichota_2014_table2_luc_dmy.csv`
- Variables: annual DMY by region × LUC class (2/4/6), plus expert-estimated DMI
  (potential/top farmer/average farmer) for cross-check
- Decision supported: Waikato pasture growth curve annual magnitude — 8493 kg DM/ha/yr,
  LUC Class 6 (steep hill), confirmed exact match to source Table 2
- ⚠ Monthly *shape* for this region is NOT in this source as a data table — Figure 2 in
  the paper is a chart, not printed numbers. Digitizing it remains an open task (see
  FORMULAS.md Named Gaps). Shape now comes from a different real source — see King
  Country entry below.
- Status: **LIVE** — magnitude figure applied in `pasture_growth_curve.csv`.

**"Pasture Plan growth rate 2002-2003" (King Country) — real shape for Waikato**
- Retrieved from agyields.co.nz dashboard, 2026-07-17. Raw data (80 rows, 3 exact
  duplicates flagged not removed, for transparency):
  `data/raw/reference/pasture_growth_sources/agyields_raw/196-657-download-17Jul2026.csv`
- Cleaned/deduped source file (77 unique rows):
  `data/raw/reference/pasture_growth_sources/king_country_pasture_plan_2002_2003.csv`
- Sites: Paddock Flat, Paddock Oat — Waikato region, King Country specifically, same
  name as the South_Waikato_King_Country target region and a tighter geographic match
  than Cichota's pooled Pukekohe/Ruakura/Whatawhata sites.
- Decision supported: **replaces Waikato's flat placeholder shape.** Real monthly-shape
  data, rescaled onto Cichota's 8493 kg DM/ha/yr magnitude (rescale math in
  `build_pasture_growth_curve.py`, `rescale_shape_to_magnitude()`). This source's own
  implied annual total (~11,868 kg DM/ha/yr, single season) is not used directly —
  Cichota's 30-year simulated magnitude is more robust, so only the *shape* (relative
  month-to-month pattern) is borrowed and rescaled.
- ⚠ Single season (2002–2003), two paddocks. A real upgrade from the flat placeholder,
  not a multi-year-verified curve — flag this if precision matters downstream.
- Status: **LIVE** — shape applied, rescaled, in `pasture_growth_curve.csv`.

**Auckland Council TR2017/020 (Hicks & Curran-Cournane, 2017), Appendix 2**
- Full citation: `CITATIONS.md`
- Source file (transcribed 2026-07-17, all 207 appendix rows, not just the 2 used):
  `data/raw/reference/pasture_growth_sources/tr2017_020_appendix2_pasture_yields.csv`
- Variables: pasture growth (un-improved/semi-improved/improved, t DM/ha/yr) and stocking
  rate (SU/ha) by geology × landform × LUC class, for all of Auckland region
- Decision supported: West Auckland annual magnitude (6900 kg DM/ha/yr) = average of the
  "regolithic footslopes" semi-improved rows for "banded or massive sandstone" (6.3 t/ha)
  and "claystone, mudstone, shale" (7.5 t/ha); `lifestyle_flat` carrying capacity (9.0
  SU/ha) = average of the same two rows' semi-improved stocking rate (8 and 10 SU/ha)
- ⚠ No monthly shape data in this source either — confirmed by full-text search, this
  report cites Cichota's method rather than providing its own seasonal curve. Shape now
  comes from a different real source — see combined Welsford+kikuyu entry below.
- Status: **LIVE** — magnitude and carrying capacity verified against the full extracted
  table; remains the magnitude anchor (shape borrowed elsewhere, not this source).

**Welsford (Auckland) + Northland kikuyu, combined — real shape for West Auckland**
- Welsford raw: `data/raw/reference/pasture_growth_sources/agyields_raw/Pasture_Plan_growth_rate_2002_2003__Welsford_.csv`
  (Auckland region, Rodney District, 2002-2003, sites Lower Yards + Woolshed)
- Kikuyu raw (196 dataset only): `data/raw/reference/pasture_growth_sources/agyields_raw/196-download-17Jul2026.csv`
  (Northland, 2016, "Beef Profit from Pasture Group: Technical Summary 2")
- Combined/cleaned: `data/raw/reference/pasture_growth_sources/west_auckland_combined_shape_welsford_kikuyu.csv`
- Decision supported: **replaces West Auckland's flat placeholder shape.** Welsford covers
  Jan–May and Aug–Dec (real, same region as the target, but ~70km north of West Auckland
  and different local geology to TR2017/020's regolithic footslopes). Kikuyu-196 covers
  Apr–Sep (real, species-matched to West Auckland's dominant lifestyle-block pasture, but
  wrong region — Northland). Combined, every month has at least one real source; the
  Apr/May/Aug/Sep overlap is averaged between the two rather than picked arbitrarily.
- ⚠ A related dataset ("228" — grazing rotation length on kikuyu, 1982-84) was
  **excluded**: its date ranges span 4-5 months per row (a rotation-length experiment,
  not seasonal measurement) and are not usable as monthly data. Do not re-include it
  without re-deriving true monthly rates from the underlying trial design.
- ⚠ Welsford (2002-03) and kikuyu (2016) are ~14 years apart. Flagged as mainly a
  magnitude-comparability risk (fertiliser/cultivar practice may have shifted) — lower
  risk for the seasonal shape itself, and moot in any case since magnitude is anchored to
  TR2017/020, not to either of these sources.
- Status: **LIVE** — shape applied, rescaled onto TR2017/020's 6900 kg DM/ha/yr, in
  `pasture_growth_curve.csv`.

**DTT Stratford (Dairy Trust Taranaki) — real monthly pasture growth, Taranaki**
- Retrieved from agyields.co.nz dashboard, 2026-07-17. Raw data:
  `data/raw/reference/pasture_growth_sources/agyields_raw/640-download-17Jul2026.csv`
  (130 rows, ~monthly intervals, 2015–2025). Aggregated to clean monthly means:
  `data/raw/reference/pasture_growth_sources/dtt_stratford_taranaki_monthly_growth.csv`
- Original source: https://www.dairytrusttaranaki.co.nz/wp-content/ (full URL in raw file)
- Decision supported: **replaces the fabricated Taranaki entry.** This is now Taranaki's
  primary magnitude AND shape source — 10 years of real monthly data, spring peak ~68–70
  kg DM/ha/day (Sep–Oct), winter trough ~12.6 (June).
- ⚠ DTT = Dairy Trust Taranaki — this is a dairy research site, so a dairy-proxy caveat
  still applies to grazing type. The difference from the fabricated version: this is a
  real, dated, Taranaki-specific, publicly-sourced dataset, not an invented citation.
- Status: **LIVE** — real data, replaces prior fabrication. Not yet wired into
  `pasture_growth_curve.csv` (pending rebuild).

**Reardon (1978) — beef pasture, Te Kuiti & Whatawhata, Waikato**
- Retrieved from agyields.co.nz, 2026-07-17:
  `data/raw/reference/pasture_growth_sources/reardon_1978_waikato_beef_crosscheck.csv`
- 4 rows, annual, 1971/1974. Both sites are inside the South_Waikato_King_Country region
  boundary (Te Kuiti is the region's anchor town).
- Decision supported: independent, genuinely beef-specific cross-check on Cichota's
  Waikato magnitude. Too sparse (n=4, 50 years old) to replace Cichota as primary — use
  as a footnoted sanity check only.
- Status: **LIVE**, secondary/cross-check use only.

**Ballantrae Research Station (López et al., 2003) — sheep hill country, Whanganui-Manawatu**
- Retrieved from agyields.co.nz, 2026-07-17:
  `data/raw/reference/pasture_growth_sources/ballantrae_whanganui_manawatu_hillcountry.csv`
- 11 rows, annual only, one year (Jul 1997–Jul 1998), 11 slope/fertility/stocking
  treatments. Real sheep-grazed hill country, Whanganui-Manawatu — adjacent to but not
  the same as the Taranaki/N. Whanganui target region.
- Decision supported: secondary sanity check on DTT Stratford's dairy-farm-derived
  Taranaki figures against genuine hill-country sheep numbers. Not primary — wrong
  sub-region, single year, no monthly resolution.
- Status: **LIVE**, secondary/cross-check use only.

**Fielding "Pasture Plan" 2002–2003 — Deightons & Kowhais, Whanganui-Manawatu**
- Retrieved from agyields.co.nz, 2026-07-17:
  `data/raw/reference/pasture_growth_sources/fielding_manawatu_pasture_plan_2002_2003.csv`
- 72 rows, roughly-monthly intervals (24–53 day spans), one season only. Grazing
  type/species not specified in source metadata.
- Decision supported: another Manawatu-region secondary cross-check, same caveats as
  Ballantrae above.
- Status: **LIVE**, secondary/cross-check use only.

- Status: **LIVE**, secondary/cross-check use only.

**Note:** `northland_kikuyu_growth_rate.csv` (34 rows, both the "196" and the excluded
"228" datasets) was the original scouting file for the kikuyu shape idea. It's superseded
by the combined Welsford+kikuyu entry above, which uses only the valid "196" subset and
is the version actually wired into `pasture_growth_curve.csv`. Kept on disk for
provenance, not a live source in its own right.

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