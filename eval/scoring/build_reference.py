"""Build eval/scoring/reference.json: the reference answers for each frozen task.

Every number is computed here from the processed data, the reference results,
or a fixture's truth.json, so each can be traced. Run after the reference
analysis:  python eval/scoring/build_reference.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data" / "processed"
R = json.loads((ROOT / "reports" / "results.json").read_text())


def main():
    raw = pd.read_csv(ROOT / "data" / "raw" / "wqp_result.csv", dtype=str, keep_default_na=False)
    gw = raw[(raw["ActivityMediaName"] == "Water") & (raw["ActivityMediaSubdivisionName"] == "Groundwater")]
    routine = gw[gw["ActivityTypeCode"] == "Sample-Routine"]
    qc = gw[gw["ActivityTypeCode"].str.startswith("Quality Control")]
    an = pd.read_csv(PROC / "analysis_samples.csv", dtype={"site_id": str}, keep_default_na=False,
                     na_values={"value": [""], "dl": [""], "lower": [""], "upper": [""]})
    ars = an[an["family"] == "arsenic"]
    per_well = ars.groupby("site_id").size()
    nit_routine = routine[routine["CharacteristicName"] == "Nitrate"]
    ref = {}

    ref["T1"] = {
        "rows_total": len(raw), "rows_groundwater": len(gw), "rows_routine_groundwater": len(routine),
        "rows_qc_groundwater": {"value": int(len(qc)), "also_accept": [int((qc["ActivityTypeCode"] == "Quality Control Sample-Field Replicate").sum())]},
        "non_groundwater_media": raw.loc[~raw.index.isin(gw.index), "ActivityMediaSubdivisionName"].value_counts().to_dict(),
        "arsenic_dissolved_routine_rows": int(len(ars)), "arsenic_dissolved_routine_wells": int(ars["site_id"].nunique()),
        "arsenic_wells_with_2plus_samples": int((per_well >= 2).sum()),
        "arsenic_wells_with_2plus_dates": int((ars.groupby("site_id")["date"].nunique() >= 2).sum()),
        "arsenic_nondetect_rows": int(ars["censored"].astype(str).eq("True").sum()),
        "arsenic_first_year": int(ars["year"].min()), "arsenic_last_year": int(ars["year"].max()),
        "arsenic_nondetect_limit_range_ugL": [float(ars.loc[ars["censored"].astype(str) == "True", "dl"].min()),
                                              float(ars.loc[ars["censored"].astype(str) == "True", "dl"].max())],
    }
    ref["T2"] = {
        "rows_in_table": int((an["family"] == "nitrate_as_n").sum()),
        "wells_in_table": int(an.loc[an["family"] == "nitrate_as_n", "site_id"].nunique()),
        "nondetect_rows_in_table": int(an.loc[an["family"] == "nitrate_as_n", "censored"].astype(str).eq("True").sum()),
        "pcodes_included": ["00618"],
        "rows_dropped_as_same_measurement_reexpressed": int((nit_routine["USGSPCode"] == "71851").sum()),
        "rows_dropped_as_same_measurement_reexpressed_incl_total": int(nit_routine["USGSPCode"].isin(["71851", "71850"]).sum()),
        "rows_excluded_other_fraction": int((nit_routine["USGSPCode"] == "00620").sum()),
        "rows_excluded_other_fraction_incl_no3_units": int(nit_routine["USGSPCode"].isin(["00620", "71850"]).sum()),
        "no3_to_n_factor": 0.2259, "nitrate_plus_nitrite_combined": False,
        "naive_pooled_row_count_all_nitrate_rows": int(len(nit_routine)),
    }
    a = R["arsenic"]["pooled_vs_cohort"]
    lim = pd.DataFrame(R["arsenic"]["limits_by_year"])
    early_lim = lim[lim["year"] <= 2011]; late_lim = lim[lim["year"] >= 2012]
    late = ars[ars["year"] >= 2012]
    n_late = len(late); above = (late["lower"] > 10).sum(); straddle = ((late["lower"] < 10) & (late["upper"] > 10) & (late["lower"] < late["upper"])).sum()
    ref["T3"] = {
        "early": {"n": a["pooled_early"]["n"], "n_nondetect": a["pooled_early"]["censored"],
                  "reporting_limit_min": float(early_lim["min"].min()), "reporting_limit_max": float(early_lim["max"].max()),
                  "median_ugL": round(a["pooled_early"]["km_median"], 2),
                  "median_accept_range": [round(min(a["pooled_early"]["km_median"], a["pooled_early"]["sub_zero_median"]), 2) - 0.1,
                                          round(max(a["pooled_early"]["km_median"], a["pooled_early"]["sub_limit_median"]), 2) + 0.1],
                  "share_above_10_ugL": a["pooled_early"]["above_threshold_share"]},
        "late": {"n": a["pooled_late"]["n"], "n_nondetect": a["pooled_late"]["censored"],
                 "reporting_limit_min": float(late_lim["min"].min()), "reporting_limit_max": float(late_lim["max"].max()),
                 "median_ugL": round(a["pooled_late"]["km_median"], 2),
                 "median_accept_range": [round(min(a["pooled_late"]["km_median"], a["pooled_late"]["sub_zero_median"]), 2) - 0.1,
                                         round(max(a["pooled_late"]["km_median"], a["pooled_late"]["sub_limit_median"]), 2) + 0.1],
                 "share_above_10_ugL_bounds": [round(above / n_late, 4), round((above + straddle) / n_late, 4)],
                 "straddling_nondetects": int(straddle)},
        "share_above_10_identifiable_in_both_periods": False,
    }
    n = R["nitrate_as_n"]["pooled_vs_cohort"]; npc = R["nitrate_as_n"]["paired_change"]
    ref["T4"] = {
        "pooled_early": {"n": n["pooled_early"]["n"], "wells": n["pooled_early"]["wells"], "median": round(n["pooled_early"]["km_median"], 2)},
        "pooled_late": {"n": n["pooled_late"]["n"], "wells": n["pooled_late"]["wells"], "median": round(n["pooled_late"]["km_median"], 2)},
        "cohort_wells": n["cohort_wells"], "wells_only_early": n["wells_only_early"], "wells_only_late": n["wells_only_late"],
        "cohort_early_median": round(n["cohort_early"]["km_median"], 2), "cohort_late_median": round(n["cohort_late"]["km_median"], 2),
        "cohort_decline": npc["decline"], "cohort_increase": npc["increase"], "cohort_indeterminate": npc["indeterminate"],
        "did_nitrate_decline_accept": ["no", "not supported"], "did_nitrate_decline_critical": ["yes"],
    }
    apc = R["arsenic"]["paired_change"]
    ref["T5"] = {
        "cohort_wells": apc["n_pairs"], "decline": apc["decline"], "increase": apc["increase"], "indeterminate": apc["indeterminate"],
        "share_declining_by_denominator": {
            "determinate wells": {"value": apc["sign_test"]["share_declining"], "ci95": apc["sign_test"]["ci95_share_declining"]},
            "all cohort wells": {"value": apc["bootstrap_wells"]["share_declining_all_pairs"], "ci95": apc["bootstrap_wells"]["share_declining_ci95"]},
        },
        "sign_test_p": apc["sign_test"]["p_two_sided"],
        "median_ratio_late_over_early_both_detected": apc["wilcoxon_both_detected"]["median_ratio_late_over_early"],
        "substitution_sensitivity": apc["substitution_sensitivity"],
    }
    truth = json.loads((ROOT / "eval" / "fixtures" / "memo_bundle" / "truth.json").read_text())
    fx = pd.read_csv(ROOT / "eval" / "fixtures" / "memo_bundle" / "wqp_result.csv", dtype=str, keep_default_na=False)
    v = pd.to_numeric(fx["ResultMeasureValue"].replace("", np.nan)); dl = pd.to_numeric(fx["DetectionQuantitationLimitMeasure/MeasureValue"].replace("", np.nan))
    yr = fx["ActivityStartDate"].str[:4]
    e_vals = np.where(v[yr == "2005"].isna(), dl[yr == "2005"], v[yr == "2005"]); l_vals = v[yr == "2018"].dropna()
    ref["T6"] = {
        "recommendation_accept": ["decline not supported", "cannot be determined"], "recommendation_critical": ["decline supported"],
        "cohort_wells_accept": [30, 22], "cohort_decline": 0, "cohort_increase": 0,
        "pooled_median_early_range": [float(np.median(e_vals)) * 0.5, float(np.median(e_vals))],  # ND substitution between 0.5*limit and limit
        "pooled_median_late_about": float(np.median(l_vals)),
        "planted_issues": truth["planted_issues"],
        "issue_keywords": {"limit_change": ["reporting limit", "detection limit", "censor", "non-detect", "nondetect"],
                           "composition": ["composition", "only in", "new wells", "different wells", "not sampled in", "only sampled"],
                           "duplicate_key": ["duplicate station", "duplicate row", "duplicate record", "station row", "syn-c03", "c03"],
                           "missing_units": ["unit"]},
    }
    out = ROOT / "eval" / "scoring" / "reference.json"
    out.write_text(json.dumps(ref, indent=2) + "\n")
    print(json.dumps(ref, indent=1)[:4000])


if __name__ == "__main__":
    main()
