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