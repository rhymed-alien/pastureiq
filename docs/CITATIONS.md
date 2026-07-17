# CITATIONS.md — PastureIQ

Every source cited anywhere in PROJECT_SPEC.md, MRS.md, or FORMULAS.md. One entry per
source: what it is, what it's used for, where in the project. This is the single home for
bibliography — MRS Section 2.3 should point here rather than restate the list.

Status key: **CITED** = referenced for a design decision, no raw data pulled ·
**DATA SOURCE** = also appears in DATA_SOURCES.md as an actual dataset ·
**PENDING PERMISSION** = citable but formal permission not yet confirmed.

---

## Stock Unit / LSU Basis (Group A)

**Coop, I.E. (1965).** Standard ewe definition — foundational basis of the NZ stock unit
system. **Used for:** LSU = 1.0 ewe baseline. **Status:** CITED.

**Parker, W.J. (1998).** *Standardisation between livestock classes: use and misuse of the
stock unit system.* **Used for:** LSU baseline (6000 MJME/yr, 520 kg DM/yr), definitional
basis for cross-class conversion. **Status:** CITED.

**RuralHQ (2019).** Modern NZ standard ewe / LSU reference figures. **Used for:** confirms
1 LSU = 6000 MJME/yr = 520 kg DM/yr baseline. **Status:** CITED.

**Otago Regional Council memo (2023),** citing Parker (1998). **Used for:** secondary
confirmation of LSU baseline. **Status:** CITED.

**B+LNZ Sheep & Beef Farm Survey — Stock Unit Conversions** (supplied directly by B+LNZ
Economic Service, email, 2026-06-24). **Used for:** `lsu_conversion_table.csv`, all
per-class LSU values (ewe, hogget, ram, wether, full cattle range). **Status:** DATA
SOURCE — see DATA_SOURCES.md. Provenance in `docs/blnz_lsu_source_record.md`.

**B+LNZ Fact Sheet 90 (FS90).** **Used for:** cattle LSU derivation; terrain feed-cost
uplift reference (hard hill cow ~65 MJME/day vs ~55 easy hill) — figure not yet quantified
into code, flagged as a named gap in FORMULAS.md Group B. **Status:** CITED, partially
applied.

**B+LNZ Fact Sheet 83 (FS83).** **Used for:** terrain feed-cost uplift reference (+0.5 MJME
steep-country sheep). **Status:** CITED, not yet applied.

---

## Pasture Growth Model (Group B)

**Cichota, R. et al. (2014).** APSIM simulation, LUC Class 6 (steep hill), rotational
grazing modelled explicitly as a sheep and beef system, Waikato/Canterbury/Southland.
**Used for:** Waikato pasture growth curve — annual magnitude anchor (8493 kg DM/ha/yr),
scale factor 0.4819 applied to the DairyNZ shape curve. First sheep/beef-anchored figure
in the project. **Status:** CITED, applied.

**Hicks, D. & Curran-Cournane, F. (2017).** Auckland Council Technical Report TR2017/020,
Appendix 2 — field-trial pasture yields by landform/geology/management level. **Used for:**
West Auckland pasture growth curve — annual magnitude anchor (6900 kg DM/ha/yr), landform
matched to regolithic footslope / Waitemata Group geology. Also source for `lifestyle_flat`
carrying capacity (4.5–15.5 SU/ha). **Status:** CITED, applied.

**DairyNZ Ruakura/Newstead (1996–2017 avg).** Dairy pasture growth curve. **Used for:**
monthly *shape* only (not magnitude) for Waikato and West Auckland — a proxy, flagged
explicitly as unresolved (dairy farm type, not sheep/beef). **Status:** CITED, proxy —
not a real fix.

**DairyNZ Hawera WTARS.** Dairy pasture growth curve, Taranaki. **Used for:** Taranaki
growth curve, both shape AND magnitude — the one region with no sheep/beef-specific
upgrade found. **Status:** CITED, full proxy caveat still applies.

**Woodward, S.J.R. et al.** *NZ Journal of Agricultural Research* — weather-driven pasture
growth relationships. **Used for:** reasoning behind the water-surplus adjustment heuristic
(not a fitted model — no labelled ground-truth data exists for the target regions).
**Status:** CITED.

**Amies, A. et al. (2021).** *National Mapping of NZ Pasture Productivity Using Temporal
Sentinel-2 Data.* https://doi.org/10.3390/rs13081481. **Used for:** future NDVI-based
pasture cover estimation (candidate method for the cover-estimation gap in Group C2 — not
yet built). **Status:** CITED, forward reference only.

---

## Market & Price (Group D)

**B+LNZ Farmgate Price Trends.** **Used for:** Group D market signal, `price_vs_seasonal`.
**Status:** DATA SOURCE — see DATA_SOURCES.md. ⚠ Coverage/access status needs reconciling
against actual repo state before relying on this entry.

**B+LNZ Stock Number Survey** (as at 30 June 2025). **Used for:** regional stock-number
context (Northland–Waikato–BoP and Taranaki–Manawatū coarse regions), and the
pastoral-grazing-≈-85%-of-farm-area figure that supports `effective_hectares` definition.
**Status:** PENDING PERMISSION — carries "no reproduction without permission"; citation
permission to be confirmed via B+LNZ contact.

**B+LNZ Lamb Crop Report 2025.** **Used for:** regional feed commentary, lamb crop and ewe
performance context. **Status:** PENDING PERMISSION — same copyright caveat as above.

**B+LNZ New Season Outlook 2024–25.** **Used for:** market/seasonal context. **Status:**
CITED, not yet directly used in code.

**B+LNZ Farm Facts 2023.** **Used for:** general farm-class and production context.
**Status:** CITED, not yet directly used in code.

**Treasury NZ, FEU Special Topic — NZ Meat Exports (2025).** **Used for:** export market
context, cross-validation candidate for price signals. **Status:** CITED, not yet used.

---

## Weather Forecast Skill (Group F — confidence model)

**American Meteorological Society (AMS).** **Used for:** basis for "no useful daily skill
beyond ~8 days" — underpins the HIGH confidence tier (7-day horizon). **Status:** CITED.

**Riemer, M. et al. / Johannes Gutenberg University (JGU).** **Used for:** 14-day forecast
skill ceiling, error-doubling-every-~5-days figure — underpins MEDIUM confidence tier.
**Status:** CITED.

**The Weather Company.** **Used for:** ~90% skill at 5 days, ~80% at 7 days — underpins
HIGH confidence tier figures (0.85). **Status:** CITED.

**S2S (Subseasonal-to-Seasonal) hydropower study.** **Used for:** 4-week average
precipitation retains fair skill even when daily forecasts don't — underpins LOW/OUTLOOK
confidence tier (0.40) and the design rule that 4-week output must read as trend, not
daily forecast. **Status:** CITED.

**Zippenfenig, P. (2023).** *Open-Meteo.com Weather API.*
https://doi.org/10.5281/zenodo.7970649. **Used for:** attribution for the Open-Meteo
historical weather pull. **Status:** DATA SOURCE — see DATA_SOURCES.md.

---

## Forecasting Methodology (Group D/MP3)

**Taylor, S.J. & Letham, B. (2018).** *Forecasting at Scale* (Facebook Prophet).
https://doi.org/10.1080/00031305.2017.1380080. **Used for:** planned Prophet model for
price direction forecasting (`src/price_forecast.py`, not yet built — MP3). **Status:**
CITED, forward reference only.

---

## Regional / Farm Context

**Rural Leaders NZ (2019).** *Technology use by sheep and beef farmers.* **Used for:**
context on farmer technology adoption / time-poor decision-making framing. **Status:**
CITED.

**Rural Leaders NZ (2025), Campbell-Smith.** *Technology adoption on NZ sheep and beef
farms.* **Used for:** same, updated context. **Status:** CITED.

**Taranaki Regional Council (2022).** *State of Environment 2022.* **Used for:** Taranaki
regional context (papa soil, rainfall patterns feeding the FEP disclaimer). **Status:**
CITED.

**Stats NZ (2022).** *Agricultural Production Census.* **Used for:** farm counts and
livestock numbers per region, documentation context. **Status:** CITED, dataset not yet
pulled — see DATA_SOURCES.md.

---

## Dead Ends (logged so they aren't re-chased)

**NZ Meat Board slaughter page.** Redirects to B+LNZ — not an independent source.
**Status:** DEAD END, logged 2026-06-24.

**Rabobank agri reports.** PDF-only commentary, no raw data. **Status:** DEAD END, logged
2026-06-24.

---
*Citations reference sheet v1.0 — built from PROJECT_SPEC.md, MRS.md Section 2.3, and
FORMULAS.md source notes. Add new sources here as they're cited; MRS Section 2.3 should
only checkbox-point here, not restate entries.*