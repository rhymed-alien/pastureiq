# Appendix: Pasture Growth Data Sources Evaluated

## Purpose

FORMULAS.md originally specified Group B (pasture supply) as "a trained model
(regression/XGBoost)." This assumed a labeled ground-truth dataset — actual observed
pasture growth rate, dated, by region — to train against. No such dataset was assumed
to exist for PastureIQ's three target regions (South Waikato/King Country, South
Taranaki/N. Whanganui, West Auckland) without verification.

This appendix documents the search: what was checked, what was found, and why each
source was accepted, adapted, or rejected. The goal is an honest record of the process,
not just the outcome — so the same ground isn't re-covered later, and so the final
model's provenance is traceable.

## Sources evaluated

### 1. DairyNZ regional pasture growth data (published PDFs)

| Region proxy | Site | Period | Granularity |
|---|---|---|---|
| South Waikato/King Country | Ruakura/Newstead | 1996–2017 (multi-year avg) | Monthly average |
| South Taranaki/N. Whanganui | Hawera WTARS | 2008–2016 (multi-year avg) | Monthly average |
| West Auckland | — | — | No direct dataset exists |

**Verdict: adopted as the seasonal baseline (Group B "Option A" — sourced curve +
heuristic weather adjustment, not a trained model).**

Waikato and Taranaki figures were cross-confirmed by independently retrieving the same
site data from two separately-hosted DairyNZ PDFs; values matched exactly. West Auckland
has no direct DairyNZ coverage — confirmed absent from DairyNZ's own regional resource
index. Northland (Dargaville-NARF) was checked as the nearest geographic proxy, but two
DairyNZ documents gave conflicting figures for the same site and the 12-value sequence
did not resolve to a clean Jan–Dec order — not force-fit into the model.

**Caveat carried forward:** this is *dairy* pasture data. DairyNZ's own source PDF states
the figures "may include nitrogen fertiliser." Hill-country sheep/beef pasture is
typically extensive and unfertilised. The seasonal *shape* (spring flush, winter trough)
likely transfers; the absolute kg DM/ha/day levels are probably optimistic for
unfertilised hill country. This is a stated assumption, not a validated one.

### 2. AgYields National Database — bulk multi-region export (428 rows)

A general bulk download covering Waikato, Taranaki, Bay of Plenty, Northland,
Canterbury, and Southland across several underlying studies.

| Region | Rows | Date range | Overlap with weather data (2015–) | Farm type |
|---|---|---|---|---|
| Waikato (King Country) | 171 | 1973–2012 | **0 of 171** | Sheep/beef (confirmed) |
| Taranaki (DTT Stratford) | 157 | 2003–2025 | **130 of 157** | Dairy (research station) |
| Northland (Auckland proxy) | 7 | single 2011 season | **0 of 7** | Not stated |
| Bay of Plenty | — | 1989–1991 | 0 | Not a target region |
| Canterbury / Southland | — | 2011 only | 0 | Not target regions |

**Verdict — Waikato (King Country): rejected for model training, retained as a baseline
citation.** All rows predate the project's weather dataset (2015–) entirely — there is no
year with both a growth observation and matching weather data. However, the source is
genuine: B+LNZ-funded, on-farm, AgResearch-supported sheep-and-beef data (Clarke-Hill &
Fraser, 2007), explicitly tagged "Sheep/Beef" in the source metadata. This is a
farm-type-correct alternative to DairyNZ's dairy-flat Ruakura baseline, even though its
age (2002–03) rules it out for weather-matched training. Recommendation for future work:
adopt as the Waikato seasonal-shape reference in place of (or alongside) the DairyNZ
figure, while keeping the DairyNZ data for its currency.

**Verdict — Taranaki (DTT Stratford): the one genuine training-data candidate found.**
Monthly granularity confirmed by inspecting row structure directly (one annual summary
row plus twelve real monthly rows per year), spanning 2015–2025 — roughly 130 real
(weather, growth) pairs, fully within the project's weather data window. Caveat: source
is Dairy Trust Taranaki, a dairy research station — the same dairy-vs-hill-country
proxy issue as the DairyNZ data applies here too. Logged as a named MP3 upgrade path:
a genuinely trained model is achievable for this one region, not project-wide.

**Verdict — Northland (Auckland proxy): rejected.** Single season, seven rows, no
weather overlap, farm type not stated. No improvement over the DairyNZ Northland dead
end already documented.

**Data-quality note:** a stray text-encoding artifact was found in the
`Published/unpublished` column (an invisible-character variant of "Unpublished" counted
as a separate category from the clean value). Minor, but worth a `.strip()` on ingest if
this file is used directly.

### 3. AgYields — Ballantrae Research Station (Whanganui-Manawatu, 11 rows)

López, Lambert, Mackay & Valentine — "The influence of topography and pasture
management on soil characteristics and herbage accumulation in hill pasture in the
North Island of New Zealand" (DOI: 10.1023/A:1026062502566).

**Verdict: rejected for model training, retained as supporting evidence for a different
open problem.** All 11 rows share an identical date span (01/07/1997–01/07/1998) — this
is not a time series, it is eleven spatial plots measured once in the same year. 28
years old, zero weather-data overlap.

However, the site itself is genuine hill-country sheep research (Ballantrae is a
dedicated AgResearch hill-country station; defoliation method recorded as "grazed by
ewes"). The finding is directly relevant elsewhere in the project: growth rate varies
**6× (7.87 to 47.19 kg DM/ha/day) across plots at the same site in the same year**,
attributable to topography alone. This is real, citable evidence for the
terrain-differentiated design already assumed in `terrain_carrying_capacity.csv` and the
still-open `MIN_RESIDUAL_COVER_BY_TERRAIN` table — worth citing in the methodology
section as justification for that design choice, and the underlying paper is a
candidate source if per-slope-class multipliers are needed later.

**Geographic caveat:** labeled "Whanganui-Manawatu," but Ballantrae's coordinates
(-40.32, 175.83) sit well south of the project's actual target area (South
Taranaki/N. Whanganui, centred near -39.63, 174.93) — closer to Manawatu/Woodville than
North Whanganui. Same broad region label, not the same hill country; not treated as
regionally representative.

### 4. AgYields — Poukawa on-farm research (Hawke's Bay, 24 rows)

"On Farm Pasture Growth rate – Ryegrass 2022–2024," On-Farm Research, Poukawa.

**Verdict: rejected — wrong region, not a data-quality issue.** Structurally this is the
best-shaped file found (24 rows, monthly, 2022–2024, 100% within the weather-data
window) — but Poukawa is in Hawke's Bay, 159–374 km from the three target regions and,
more materially, on the opposite (eastern, rain-shadow) side of the North Island's
central ranges from Taranaki and Waikato. Hawke's Bay's dry-summer climate is not a
reasonable proxy for the project's western/central high-rainfall target regions —
distance alone understates the mismatch. Secondary concerns: unpublished (sourced from a
farmer-run monitoring website, not a peer-reviewed trial) and farm type not stated
(sown ryegrass, type unspecified). Region was the deciding factor, not publication
status or farm type — noted here since it would be easy to mis-weight these three
concerns in the opposite order.

### 5. Cichota, Vogeler, Li & Beautrais (2014) — APSIM-simulated pasture growth curves by Land Use Capability class

R. Cichota, I. Vogeler, F.Y. Li and J. Beautrais, "Deriving pasture growth patterns for
Land Use Capability Classes in different regions of New Zealand," *Proceedings of the New
Zealand Grassland Association* 76: 203–210 (2014).

**Verdict: adopted — the first genuinely sheep/beef-anchored source found in this project.**
AgResearch used APSIM (a validated agricultural simulation model, cross-checked against
long-term pasture measurements at Ruakura and Whatawhata among other sites) to derive
seasonal pasture growth curves by LUC Class, across three regions: **Waikato, Canterbury,
and Southland**. The pasture was explicitly modelled as "a mixture of perennial ryegrass,
white clover, and different proportions of low fertility tolerant species," cut every 3
weeks to a 1250 kg DM/ha residual, "mimicking rotational grazing of a **sheep and beef
system**" — the first source in this search that is genuinely farm-type-correct for this
project, not a dairy substitute.

Waikato is directly one of the three regions studied. Table 2 gives real annual DMY by LUC
class for Waikato: Class 2 (flat) = 13,941 kg DM/ha/yr; Class 4 (moderate) = 11,270; Class
6 (steep hill) = 8,493. LUC6 was adopted as the annual-total anchor for this project's
Waikato/King Country region, since it matches the described hill-country terrain. Taranaki
and Auckland are not covered by this paper — no windfall for those two regions.

**Limitation:** the paper gives annual totals precisely (Table 2) and seasonal curves as a
figure (Figure 2), not a monthly table — the monthly *shape* still had to be borrowed from
elsewhere (see FORMULAS.md Group B). Also worth noting: the paper itself flags that
Ruakura's real observed pasture growth ran higher than its LUC2 simulation in summer,
attributed to paspalum's higher summer growth versus the ryegrass-only pasture assumed in
the simulation — a reminder that even this improved source has known local discrepancies.

### 6. Hicks & Curran-Cournane (2017) — Auckland Council Technical Report 2017/020

Douglas Hicks and Fiona Curran-Cournane, "Matching farm production data to land use
capability for Auckland," Auckland Council Technical Report 2017/020.

**Verdict: adopted — resolves West Auckland for both the growth curve and carrying
capacity, from one source.** Unlike Cichota et al., this report does not run a simulation —
it compiles **real field-trial pasture yield data** (Appendix 1 lists ~50 named trial sites
across greater Auckland/Northland, mostly MAF/DSIR trials from the 1970s–1990s plus some
DairyNZ/B+LNZ monitor-farm data) and scales it to Auckland's specific landforms and
geology using empirically-derived adjustment factors for slope, instability, drainage, and
rainfall (Sections 4.1–4.5). Appendix 2 gives the output: pasture yield (t DM/ha/yr) and
stocking rate (SU/ha) at three management levels (un-improved/semi-improved/improved),
broken out by landform and geology across the whole region.

West Auckland's lifestyle-block belt (Kumeu/Waimauku/Muriwai) sits on Waitemata Group
geology — interbedded sandstone and mudstone/shale. The "FOOTSLOPES, SPURS AND RIDGES"
section of Appendix 2 was used, averaging the "banded or massive sandstone" and
"claystone, mudstone, shale" rows at "regolithic footslope" (LUC4), semi-improved column
(matching typical lifestyle-block management — grazed but not intensively farmed). This
gives: annual total 6,900 kg DM/ha/yr (average of 6,300 and 7,500), and a carrying-capacity
range of 4.5–15.5 SU/ha (un-improved to improved bounds, semi-improved midpoint 9.0) — both
adopted into the project (see FORMULAS.md Group B and `terrain_carrying_capacity.csv`).

**Limitations, stated plainly:** the landform/geology match is reasoned from regional
geology and the project's stored coordinates, not a site inspection — flagged for
validation against the project's own West Auckland farmer contacts. The report itself
warns that pasture yields are only comparable within controlled conditions (same rainfall,
landform, soil) — averaging across two geology types, as done here, is a simplification the
report's own methodology would consider a first-pass estimate, not a precise figure. No
monthly breakdown is given (annual only), same limitation as Cichota et al. above.

## Summary table

| Source | Region match | Weather-matchable | Farm type | Outcome |
|---|---|---|---|---|
| DairyNZ Ruakura | Waikato ✓ | N/A (curve, not training) | Dairy ⚠ | Shape only, as of Cichota update |
| DairyNZ Hawera WTARS | Taranaki ✓ | N/A (curve, not training) | Dairy ⚠ | Adopted (baseline), unchanged |
| DairyNZ Northland | Auckland proxy | N/A | Unknown | Rejected — conflicting data |
| AgYields King Country | Waikato ✓ | No (0/171) | Sheep/beef ✓ | Rejected for training; superseded by Cichota et al. for baseline purposes |
| AgYields DTT Stratford | Taranaki ✓ | Yes (130/157) | Dairy ⚠ | **MP3 training candidate, still open** |
| AgYields Northland | Auckland proxy | No (0/7) | Unknown | Rejected |
| AgYields Ballantrae | Whanganui-adjacent, not target | No (single year) | Sheep ✓ | Rejected for training; cited for terrain evidence |
| AgYields Poukawa | Hawke's Bay — wrong region | Yes (24/24) | Unstated | Rejected — regional mismatch |
| **Cichota et al. 2014** | **Waikato ✓ (of 3: Wai/Cant/South)** | N/A (annual + fig., not raw data) | **Sheep/beef ✓** | **Adopted — annual-total anchor for Waikato** |
| **Auckland Council TR2017/020** | **West Auckland ✓ (landform-matched)** | N/A (annual, field-trial-derived) | **Mixed, real trials** | **Adopted — annual total + carrying capacity for West Auckland** |

## Conclusion

No dataset was found that is simultaneously (a) in one of the three target regions,
(b) weather-matchable to the project's 2015– Open-Meteo data, and (c) genuine sheep/beef
hill-country pasture, at monthly or better resolution. Every dataset in this search
satisfies at most two of the three conditions.

This is the basis for Group B's current, twice-revised design: **the monthly shape of each
region's curve is still a dairy-data proxy (unresolved), but the annual magnitude is now
genuinely farm-type-correct for two of three regions** — Waikato via Cichota et al.'s
sheep/beef APSIM simulation, West Auckland via Auckland Council's real field-trial data
matched to local geology. Taranaki remains fully dairy-proxy in both shape and magnitude;
no sheep/beef-specific source was found for it in this search. Taranaki's DTT Stratford
data (Section 1 above) remains the one identified path to a genuinely trained,
non-proxy model — flagged for MP3, not attempted here since it would leave the other two
regions on a different, inconsistent methodology mid-MP2.