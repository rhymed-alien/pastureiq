# Data Sources Register

## Open-Meteo — Historical Weather API
- **Endpoint:** https://archive-api.open-meteo.com/v1/archive
- **Dataset:** ERA5 reanalysis (~25 km resolution, 1940–present)
- **Accessed:** 2026-06-08
- **Licence:** Free API non-commercial use; data licensed CC BY 4.0 (attribution required)
- **Attribution:** "Weather data from Open-Meteo.com (CC BY 4.0)"
- **Variables pulled (daily):** temperature_2m_max, temperature_2m_min, precipitation_sum,
  et0_fao_evapotranspiration, windspeed_10m_max
- **Regions:** South Waikato (-38.34, 175.16), South Taranaki (-39.63, 174.93),
  West Auckland (-36.90, 174.52)
- **Coverage retrieved:** 2015-01-01 to 2026-06-08, daily, 4177 rows per region, no missing values
- **Note:** Soil moisture/temperature NOT included — those variables proved unreliable on the
  ERA5 archive (inconsistent between forecast and historical). Soil sourcing parked for
  separate research.

## Beef + Lamb New Zealand — Stock Unit Conversions
- **Source:** B+LNZ Economic Service, Sheep & Beef Farm Survey standard conversions
- **Accessed:** 2026-06-24 (supplied directly by email in response to student data request)
- **Licence:** Provided for use in a free, non-commercial student project; B+LNZ credited as source
- **Status:** Current survey standard, **under review** — held constant for many years to
  preserve a consistent timeseries
- **Values used:** per-class stock units — sheep (ewe 1.0, hogget 0.7, wether 0.7, ram 0.8,
  grazing sheep 0.7); beef (M.A. cow 5.5, heifers/steers/bulls 3.5–5.5 by class);
  dairy grazers (R1 3.5, R2 4.5, winter cow 1.1)
- **Files:** data/raw/reference/lsu_conversion_table.csv; source record and verbatim
  email preserved in docs/blnz_lsu_source_record.md
- **Farmer decision supported:** feed demand (national, feed-only LSU baseline)
- **Caveat (per B+LNZ):** these are a general guide for policy-level implied feed utilisation,
  not a substitute for farm-level feed budgeting. Terrain effects (e.g. hard hill country)
  are applied separately as a carrying-capacity modifier, keeping LSU national and feed-only.
- **Note:** Use the Stock Units column for feed-demand maths, NOT the Cattle Equivalent column.

## Beef + Lamb New Zealand — Farmgate Price Trends [PENDING]
- **Source:** B+LNZ Economic Service (same contact as stock unit data above)
- **Status:** Requested and confirmed in progress by B+LNZ as at 2026-06-24; data awaited
- **Expected use:** market-signal layer (MP2/MP3) — farmgate price timeseries by species/class
- **Note:** Update this entry with accessed date, coverage, and licence terms on receipt.
  Log row counts, date range, and missing values after the pull, per standard practice.