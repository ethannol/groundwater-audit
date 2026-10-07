"""Generate controlled fixtures with known properties.

ALL DATA PRODUCED HERE ARE SYNTHETIC. Site identifiers start with "SYN-" and
every CSV carries a leading comment-free marker column `SYNTHETIC=1`.

Each fixture is a directory with WQP-shaped wqp_result.csv and wqp_station.csv
plus truth.json describing the planted property and the expected behaviour.
Fixtures are used (a) as invariance checks of the reference pipeline
(tests/test_fixtures.py) and (b) the `memo_bundle` fixture is the dataset for
evaluation task T6.

Run: python eval/fixtures/make_fixtures.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from gwaudit.prepare import COLS, STATION_COLS  # noqa: E402
from gwaudit.units import NO3_TO_N  # noqa: E402

HERE = Path(__file__).parent
SEED = 7


def blank_row():
    r = {c: "" for c in COLS.values()}
    r.update({
        "ActivityTypeCode": "Sample-Routine", "ActivityMediaName": "Water",
        "ActivityMediaSubdivisionName": "Groundwater", "CharacteristicName": "Nitrate",
        "ResultSampleFractionText": "Dissolved", "USGSPCode": "00618",
        "ResultMeasure/MeasureUnitCode": "mg/l as N", "ResultValueTypeName": "Actual",
        "ResultStatusIdentifier": "Accepted", "ResultAnalyticalMethod/MethodIdentifier": "SYN01",
        "LaboratoryName": "Synthetic Lab A", "ActivityStartTime/Time": "10:00:00",
    })
    return r


def make_rows(wells, early_vals, late_vals, dl_early=None, dl_late=None, lab="Synthetic Lab A"):
    """One early (2005) and one late (2018) sample per well; values below the
    limit become non-detects reported at the limit."""
    rows = []
    for i, (w, ve, vl) in enumerate(zip(wells, early_vals, late_vals)):
        for period, v, dl, year in [("E", ve, dl_early, 2005), ("L", vl, dl_late, 2018)]:
            if v is None:
                continue
            r = blank_row()
            r["MonitoringLocationIdentifier"] = w
            r["ActivityIdentifier"] = f"syn.{w}.{period}"
            r["ActivityStartDate"] = f"{year}-06-{(i % 28) + 1:02d}"
            r["ResultIdentifier"] = f"res.{w}.{period}"
            r["LaboratoryName"] = lab
            if dl is not None and v < dl:
                r["ResultMeasureValue"] = ""; r["ResultMeasure/MeasureUnitCode"] = ""
                r["ResultDetectionConditionText"] = "Not Detected"
                r["DetectionQuantitationLimitTypeName"] = "Laboratory Reporting Level"
                r["DetectionQuantitationLimitMeasure/MeasureValue"] = f"{dl:g}"
                r["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = "mg/l as N"
            else:
                r["ResultMeasureValue"] = f"{v:.3g}"
                if dl is not None:
                    r["DetectionQuantitationLimitTypeName"] = "Laboratory Reporting Level"
                    r["DetectionQuantitationLimitMeasure/MeasureValue"] = f"{dl:g}"
                    r["DetectionQuantitationLimitMeasure/MeasureUnitCode"] = "mg/l as N"
            rows.append(r)
    return rows


def station_rows(wells):
    out = []
    for w in wells:
        r = {c: "" for c in STATION_COLS.values()}
        r.update({"MonitoringLocationIdentifier": w, "MonitoringLocationName": f"synthetic well {w[-3:]}",
                  "MonitoringLocationTypeName": "Well", "HUCEightDigitCode": "00000000",
                  "LatitudeMeasure": "35.0", "LongitudeMeasure": "-117.0", "AquiferName": "Synthetic basin fill"})
        out.append(r)
    return out


def write(name, result_rows, st_rows, truth):
    d = HERE / name
    d.mkdir(exist_ok=True)
    res = pd.DataFrame(result_rows); res.insert(0, "SYNTHETIC", 1)
    st = pd.DataFrame(st_rows); st.insert(0, "SYNTHETIC", 1)
    res.to_csv(d / "wqp_result.csv", index=False)
    st.to_csv(d / "wqp_station.csv", index=False)
    truth = {"fixture": name, "synthetic": True, **truth}
    (d / "truth.json").write_text(json.dumps(truth, indent=2) + "\n")
    print(f"{name}: {len(res)} result rows, {len(st)} station rows")


def main():
    rng = np.random.default_rng(SEED)
    n = 40
    wells = [f"SYN-{i:03d}" for i in range(n)]
    base = np.exp(rng.normal(np.log(3.0), 0.6, n))  # lognormal around 3 mg/L as N

    # F0 clean: every well declines by 30%
    early, late = base, base * 0.7
    write("clean", make_rows(wells, early, late), station_rows(wells),
          {"property": "clean; every well's late value is 0.7 x its early value",
           "expected": {"cohort_wells": n, "decline": n, "increase": 0, "indeterminate": 0,
                        "median_ratio_late_over_early": 0.7, "rows_after_preparation": 2 * n}})

    # F1 unit mix: same as clean, but late values also carry an NO3-unit re-expression row (71851)
    rows = make_rows(wells, early, late)
    extra = []
    for r in rows:
        if r["ActivityIdentifier"].endswith(".L"):
            d = dict(r); d["USGSPCode"] = "71851"; d["ResultMeasure/MeasureUnitCode"] = "mg/l asNO3"
            d["ResultMeasureValue"] = f"{float(r['ResultMeasureValue']) / NO3_TO_N:.3g}"
            d["ResultIdentifier"] = r["ResultIdentifier"] + ".no3"
            d["ResultAnalyticalMethod/MethodIdentifier"] = "ALGOR"
            extra.append(d)
    write("unit_mix", rows + extra, station_rows(wells),
          {"property": "clean data plus a derived 'mg/l asNO3' row (pcode 71851) for every late sample; "
                       "the derived rows must be converted (x0.2259) and not counted as extra samples",
           "expected": {"rows_after_preparation": 2 * n, "cohort_wells": n, "decline": n, "increase": 0,
                        "median_ratio_late_over_early": 0.7, "naive_row_count_if_not_deduplicated": 3 * n}})

    # F2 duplicated join key: station table lists one well twice
    st = station_rows(wells) + [dict(station_rows(wells)[5], MonitoringLocationName="synthetic well 005 (duplicate row)")]
    write("dup_key", make_rows(wells, early, late), st,
          {"property": "station table has a duplicated MonitoringLocationIdentifier; a naive join multiplies that well's rows",
           "expected": {"rows_after_preparation": 2 * n, "rows_if_join_multiplies": 2 * n + 2,
                        "reference_pipeline_behaviour": "raises on non-unique station key"}})

    # F3 detection limit change: no true change; early limit 5, late limit 0.5
    true_vals = np.exp(rng.normal(np.log(1.0), 0.5, n))
    write("dl_change", make_rows(wells, true_vals, true_vals, dl_early=5.0, dl_late=0.5), station_rows(wells),
          {"property": "true concentrations identical in both periods; reporting limit falls from 5 to 0.5 "
                       "so most early values are non-detects (<5) and most late values are detected around 1",
              "expected": {"true_change": "none", "cohort_wells": n,
                        "decline": 0, "increase": 0,
                        "indeterminate_at_least": int(np.sum(true_vals < 5.0)) - int(np.sum(true_vals < 0.5)),
                        "substitution_half_limit_would_show": "spurious decline (2.5 -> ~1)",
                        "correct_conclusion": "change not identifiable for wells censored at 5 in the early period"}})

    # F4 composition: early period samples 20 high wells; late period samples those 20 (unchanged) plus 40 new low wells
    hi = [f"SYN-H{i:02d}" for i in range(20)]
    lo = [f"SYN-L{i:02d}" for i in range(40)]
    hi_vals = np.exp(rng.normal(np.log(8.0), 0.3, 20))
    lo_vals = np.exp(rng.normal(np.log(1.0), 0.3, 40))
    rows = make_rows(hi, hi_vals, hi_vals) + make_rows(lo, [None] * 40, lo_vals)
    write("composition", rows, station_rows(hi + lo),
          {"property": "20 high wells unchanged between periods; 40 low wells sampled only in the late period",
           "expected": {"pooled_median_early_about": round(float(np.sort(hi_vals)[(len(hi_vals) - 1) // 2]), 2),
                        "pooled_median_late_about": round(float(np.sort(np.r_[hi_vals, lo_vals])[(60 - 1) // 2]), 2),
                        "median_convention": "lower median (the Kaplan-Meier quantile convention); values rounded to 3 significant figures in the CSV",
                        "cohort_wells": 20, "decline": 0, "increase": 0, "indeterminate": 0,
                        "correct_conclusion": "pooled decline is a change in which wells were sampled, not a change at wells"}})

    # F5 missing units: one lab reports 30% of rows with blank units and blank limit units
    rows = make_rows(wells, early, late)
    k = 0
    for r in rows:
        if r["ActivityIdentifier"].endswith(".L") and k < 12:
            r["ResultMeasure/MeasureUnitCode"] = ""; r["LaboratoryName"] = "Synthetic Lab B (units not reported)"; k += 1
    write("missing_units", rows, station_rows(wells),
          {"property": "12 late-period detected results from 'Synthetic Lab B' have no unit; their magnitude is not interpretable",
           "expected": {"rows_with_missing_unit": 12, "reference_pipeline_behaviour": "raises UnitError; the analyst must exclude or abstain",
                        "cohort_wells_if_unit_missing_rows_excluded": n - 12, "decline_among_remaining": n - 12}})

    # F6 memo bundle for task T6: no true change + dl change + duplicated station key + composition + a missing-unit lab
    rng2 = np.random.default_rng(SEED + 1)
    coh = [f"SYN-C{i:02d}" for i in range(30)]
    coh_vals = np.exp(rng2.normal(np.log(1.5), 0.5, 30))
    new = [f"SYN-N{i:02d}" for i in range(30)]
    new_vals = np.exp(rng2.normal(np.log(0.6), 0.4, 30))
    rows = make_rows(coh, coh_vals, coh_vals, dl_early=2.0, dl_late=0.2) + make_rows(new, [None] * 30, new_vals, dl_late=0.2)
    k = 0
    for r in rows:
        if r["ActivityIdentifier"].endswith(".L") and r["ResultMeasureValue"] and k < 8:
            r["ResultMeasure/MeasureUnitCode"] = ""; r["LaboratoryName"] = "Synthetic Lab B (units not reported)"; k += 1
    st = station_rows(coh + new) + [dict(station_rows(coh)[3], MonitoringLocationName="synthetic well C03 (duplicate row)")]
    n_cens_early = int(np.sum(coh_vals < 2.0))
    write("memo_bundle", rows, st,
          {"property": "SYNTHETIC 'Basin Z' nitrate data for the decision-memo task. True concentrations at the 30 cohort wells are identical in both periods.",
           "planted_issues": [
               "reporting limit falls from 2.0 (early) to 0.2 (late), so early non-detects cannot be compared with late detects",
               "30 additional low-concentration wells are sampled only in the late period (composition change)",
               "station table has a duplicated site row (SYN-C03) that multiplies rows on a naive join",
               "8 late-period results from 'Synthetic Lab B' have no reported unit"],
           "expected": {"true_change": "none", "cohort_wells": 30, "early_nondetects_in_cohort": n_cens_early,
                        "decline": 0, "increase": 0,
                        "correct_memo": "a decline cannot be supported; name the limit change, the composition change, the duplicate key and the missing units",
                        "critical_error": "concluding that nitrate declined"}})


if __name__ == "__main__":
    main()
