"""
build_pasture_growth_curve.py — generates data/raw/reference/pasture_growth_curve.csv

Rebuilt 2026-07-17 after finding and removing a fabricated "DairyNZ Ruakura/Newstead"
and "DairyNZ Hawera WTARS" citation in the prior version of this file (see CHANGELOG.md,
"Pasture growth sourcing — fabrication found and corrected"). Every value below traces to
a real, checked source — see the per-region notes and DATA_SOURCES.md.

Updated same day: Waikato's flat placeholder shape replaced with a real single-season
shape (King Country 2002-2003, agyields.co.nz), rescaled onto Cichota's more robust
30-year magnitude via rescale_shape_to_magnitude().

HOW TO ADD A REGION: add one entry to REGION_SOURCES below. The key should match the
region_id used in config.py's REGIONS dict, so downstream code (pasture_model.py) can
look up a region's curve by the same key it already uses for coordinates. Re-run this
script to regenerate the CSV.

Each region needs ONE of:
  - "monthly_kgdm_ha_day": real monthly data that is ALSO the magnitude source (e.g.
    Taranaki/DTT Stratford) — used directly, annual magnitude derived from it.
  - "shape_raw_kgdm_ha_day" + "annual_magnitude_kgdm_ha_yr": a real shape from one
    source, rescaled onto a magnitude from a different, more robust source (e.g.
    Waikato: King Country shape rescaled onto Cichota's magnitude).
  - "shape": "flat" + "annual_magnitude_kgdm_ha_yr": no real monthly source exists at
    all — even split across 12 months. Explicitly NOT seasonally accurate — a flagged
    placeholder, not a proxy pretending to be one.
"""

import csv
import calendar

REGION_SOURCES = {
    "waikato": {
        "annual_magnitude_kgdm_ha_yr": 8493,
        "magnitude_source": "Cichota et al. (2014), Table 2, LUC Class 6 (steep hill), "
                             "Waikato. Verified against source PDF 2026-07-17.",
        "shape_raw_kgdm_ha_day": {
            1: 31.5, 2: 14.43, 3: 9.25, 4: 24.5, 5: 9.0, 6: 6.25,
            7: 10.57, 8: 36.12, 9: 52.62, 10: 52.5, 11: 75.88, 12: 66.75,
        },
        "shape_source": "'Pasture Plan growth rate 2002-2003 (King Country)', Paddock "
                         "Flat + Paddock Oat, agyields.co.nz, retrieved 2026-07-17. Real "
                         "measured shape, rescaled to Cichota's magnitude (see "
                         "rescale_shape_to_magnitude() below) since this source's own "
                         "single-season implied annual total (~11,866 kg DM/ha/yr) is "
                         "less robust than Cichota's 30-year simulated figure.",
        "shape_confidence": "REAL shape, rescaled — ⚠ single season (2002-2003), 2 "
                             "paddocks. An upgrade from the prior flat placeholder, not "
                             "a multi-year-verified curve.",
        "cross_check": "Reardon (1978), Te Kuiti/Whatawhata beef data — real but sparse "
                        "(n=4, 1971/1974), consistent order of magnitude, not used to "
                        "override Cichota.",
    },
    "taranaki": {
        "monthly_kgdm_ha_day": {
            1: 43.1, 2: 42.2, 3: 44.5, 4: 30.4, 5: 16.8, 6: 12.6,
            7: 23.4, 8: 51.3, 9: 69.8, 10: 68.3, 11: 59.2, 12: 46.8,
        },
        "magnitude_source": "DTT Stratford (Dairy Trust Taranaki), 10-year monthly "
                             "means (2015-2025), agyields.co.nz. Real, dated, "
                             "Taranaki-specific. Replaces a fabricated citation — see "
                             "CHANGELOG.md.",
        "shape_source": "Same source — this is real measured monthly data, not a "
                         "borrowed shape.",
        "shape_confidence": "REAL — but ⚠ DTT is a dairy research site on improved "
                             "flat/rolling land (implied annual total ~15,250 kg "
                             "DM/ha/yr). That is well above extensive sheep/beef hill "
                             "country magnitude and should be treated as an upper-bound "
                             "reference, not a direct stand-in for hill country pasture.",
        "cross_check": "Ballantrae (López et al. 2003, Whanganui-Manawatu sheep hill "
                        "country, single year 1997-98) and Fielding Pasture Plan "
                        "2002-2003 (Manawatu) — both real, both lower-magnitude than "
                        "DTT Stratford, consistent with the dairy-vs-hill-country gap "
                        "flagged above. Neither adopted as primary — wrong sub-region, "
                        "single season.",
    },
    "auckland": {
        "annual_magnitude_kgdm_ha_yr": 6900,
        "magnitude_source": "Auckland Council TR2017/020, Appendix 2 — average of the "
                             "'regolithic footslopes' semi-improved rows for 'banded or "
                             "massive sandstone' (6300) and 'claystone, mudstone, "
                             "shale' (7500). Verified against full extracted table "
                             "2026-07-17.",
        "shape_raw_kgdm_ha_day": {
            1: 55.33, 2: 37.0, 3: 57.0, 4: 71.62, 5: 68.77, 6: 44.05,
            7: 67.88, 8: 41.42, 9: 32.5, 10: 44.62, 11: 57.29, 12: 48.0,
        },
        "shape_source": "Combined real shape from two sources with complementary "
                         "monthly gaps: Welsford (Auckland region, 2002-2003) for "
                         "Jan-Mar/Oct-Dec, Northland kikuyu (2016, '196' dataset only — "
                         "the '228' rotation-length study was excluded, its date ranges "
                         "span 4-5 months at once and are not usable as monthly data) "
                         "for Jun-Jul, both averaged for the Apr/May/Aug/Sep overlap. "
                         "See west_auckland_combined_shape_welsford_kikuyu.csv for the "
                         "per-month breakdown and which source each month came from.",
        "shape_confidence": "REAL, combined from 2 real sources, no months guessed — "
                             "⚠ Welsford is 2002-2003, kikuyu is 2016 (~14 years apart). "
                             "Mainly a magnitude-comparability risk (fertiliser/cultivar "
                             "drift over time), lower risk for the seasonal shape "
                             "actually borrowed here — magnitude itself is NOT taken "
                             "from either source, TR2017/020 remains the anchor. "
                             "Welsford is also ~70km north of West Auckland (different "
                             "local geology to TR2017/020's regolithic footslopes) and "
                             "kikuyu is Northland, not Auckland — both real, both "
                             "imperfect regional matches, combined because they cover "
                             "each other's calendar gaps.",
        "cross_check": None,
    },
}


def rescale_shape_to_magnitude(raw_monthly_rate, target_annual_kgdm_ha_yr):
    """
    Rescales a real but independently-sourced monthly shape onto a more robust annual
    magnitude figure from a different source. Weights by actual days-per-month (not a
    flat /12) since raw_monthly_rate values are daily rates, not monthly totals.
    Returns {month: rescaled_kgdm_ha_day}, and the shape source's own implied annual
    total (for transparency — logged by the caller, not hidden).
    """
    days = {m: calendar.monthrange(2002, m)[1] for m in range(1, 13)}  # non-leap ref year
    shape_annual_total = sum(raw_monthly_rate[m] * days[m] for m in range(1, 13))
    scale = target_annual_kgdm_ha_yr / shape_annual_total
    rescaled = {m: round(raw_monthly_rate[m] * scale, 2) for m in range(1, 13)}
    return rescaled, round(shape_annual_total)


def build_rows():
    rows = []
    for region_id, cfg in REGION_SOURCES.items():
        if "monthly_kgdm_ha_day" in cfg:
            # Real monthly data IS the magnitude source too (e.g. Taranaki/DTT Stratford)
            monthly = cfg["monthly_kgdm_ha_day"]
            magnitude = round(sum(v * 30 for v in monthly.values()))  # approx annual
            shape_conf = cfg["shape_confidence"]
        elif "shape_raw_kgdm_ha_day" in cfg:
            # Real shape from one source, rescaled onto a more robust magnitude from
            # another source (e.g. Waikato: King Country shape -> Cichota magnitude)
            magnitude = cfg["annual_magnitude_kgdm_ha_yr"]
            monthly, shape_own_total = rescale_shape_to_magnitude(
                cfg["shape_raw_kgdm_ha_day"], magnitude
            )
            shape_conf = (cfg["shape_confidence"] +
                          f" Shape source's own implied annual total before rescaling: "
                          f"~{shape_own_total} kg DM/ha/yr.")
        else:
            magnitude = cfg["annual_magnitude_kgdm_ha_yr"]
            flat_rate = round(magnitude / 365, 2)
            monthly = {m: flat_rate for m in range(1, 13)}
            shape_conf = cfg["shape_confidence"]

        for month in range(1, 13):
            rows.append({
                "region_id": region_id,
                "month": month,
                "growth_rate_kgdm_ha_day": monthly[month],
                "annual_magnitude_kgdm_ha_yr": magnitude,
                "magnitude_source": cfg["magnitude_source"],
                "shape_confidence": shape_conf,
                "cross_check_source": cfg.get("cross_check") or "",
            })
    return rows


def write_csv(path):
    rows = build_rows()
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["# pasture_growth_curve.csv — REBUILT 2026-07-17 after removing a"])
        w.writerow(["# fabricated DairyNZ Ruakura/Hawera WTARS citation. See CHANGELOG.md"])
        w.writerow(["# and DATA_SOURCES.md (Pasture Growth section) for full provenance."])
        w.writerow(["# Generated by build_pasture_growth_curve.py — do not hand-edit values;"])
        w.writerow(["# edit REGION_SOURCES in that script and re-run instead."])
        w.writerow([])
        w.writerow(["region_id", "month", "growth_rate_kgdm_ha_day",
                     "annual_magnitude_kgdm_ha_yr", "magnitude_source",
                     "shape_confidence", "cross_check_source"])
        for r in rows:
            w.writerow([r["region_id"], r["month"], r["growth_rate_kgdm_ha_day"],
                        r["annual_magnitude_kgdm_ha_yr"], r["magnitude_source"],
                        r["shape_confidence"], r["cross_check_source"]])
    print(f"Wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    write_csv("pasture_growth_curve.csv")
    # Quick sanity print
    for region_id, cfg in REGION_SOURCES.items():
        print(f"\n{region_id}:")
        if "monthly_kgdm_ha_day" in cfg:
            for m, v in cfg["monthly_kgdm_ha_day"].items():
                print(f"  month {m:2d}: {v} kg DM/ha/day (real)")
        elif "shape_raw_kgdm_ha_day" in cfg:
            rescaled, own_total = rescale_shape_to_magnitude(
                cfg["shape_raw_kgdm_ha_day"], cfg["annual_magnitude_kgdm_ha_yr"]
            )
            for m in range(1, 13):
                print(f"  month {m:2d}: {rescaled[m]} kg DM/ha/day "
                      f"(rescaled from real shape, raw {cfg['shape_raw_kgdm_ha_day'][m]})")
            print(f"  [shape source's own implied annual total: ~{own_total} kg DM/ha/yr, "
                  f"rescaled to {cfg['annual_magnitude_kgdm_ha_yr']}]")
        else:
            flat = round(cfg["annual_magnitude_kgdm_ha_yr"] / 365, 2)
            print(f"  flat rate all months: {flat} kg DM/ha/day "
                  f"(annual {cfg['annual_magnitude_kgdm_ha_yr']}, PLACEHOLDER)")