"""Comparability and quality-control preparation of the raw WQP snapshot.

Reads data/raw/wqp_result.csv and data/raw/wqp_station.csv (never modified) and
writes to data/processed/:

    results_clean.csv     every groundwater routine-sample row, with canonical
                          units, censoring bounds, and flags (one row per source row)
    analysis_samples.csv  the subset used for trend analysis: dissolved fraction,
                          primary parameter codes only
    replicates.csv        field-replicate QC rows, same columns as results_clean
    exclusion_log.csv     every filtering step with row counts and the rule applied
    prepare_summary.json  counts and checks for the report

Every rule is explicit and logged. Nothing is dropped silently and no join may
change the row count.

Run: python -m gwaudit.prepare
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from gwaudit.units import CANONICAL_UNIT, NO3_TO_N, factor_to_canonical

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

# USGS parameter code -> (constituent family, sample fraction expected, role)
PCODE = {
    "01000": ("arsenic", "Dissolved", "primary"),
    "01002": ("arsenic", "Total", "other_fraction"),
    "00618": ("nitrate_as_n", "Dissolved", "primary"),
    "00620": ("nitrate_as_n", "Total", "other_fraction"),
    "71851": ("nitrate_as_n", "Dissolved", "derived_duplicate"),  # NO3 units, computed from 00618
    "71850": ("nitrate_as_n", "Total", "derived_duplicate"),      # NO3 units, computed from 00620
    "00631": ("no3_no2_as_n", "Dissolved", "primary"),
    "00630": ("no3_no2_as_n", "Total", "other_fraction"),
}

COLS = {
    "site_id": "MonitoringLocationIdentifier",
    "activity_id": "ActivityIdentifier",
    "activity_type": "ActivityTypeCode",
    "media": "ActivityMediaName",
    "media_sub": "ActivityMediaSubdivisionName",
    "date": "ActivityStartDate",
    "time": "ActivityStartTime/Time",
    "characteristic": "CharacteristicName",
    "fraction": "ResultSampleFractionText",
    "value_raw": "ResultMeasureValue",
    "unit_raw": "ResultMeasure/MeasureUnitCode",
    "detect_cond": "ResultDetectionConditionText",
    "dl_type": "DetectionQuantitationLimitTypeName",
    "dl_raw": "DetectionQuantitationLimitMeasure/MeasureValue",
    "dl_unit_raw": "DetectionQuantitationLimitMeasure/MeasureUnitCode",
    "pcode": "USGSPCode",
    "method_id": "ResultAnalyticalMethod/MethodIdentifier",
    "method_name": "ResultAnalyticalMethod/MethodName",
    "lab": "LaboratoryName",
    "status": "ResultStatusIdentifier",
    "value_type": "ResultValueTypeName",
    "lab_comment": "ResultLaboratoryCommentText",
    "result_comment": "ResultCommentText",
    "result_id": "ResultIdentifier",
}
STATION_COLS = {
    "site_id": "MonitoringLocationIdentifier",
    "site_name": "MonitoringLocationName",
    "site_type": "MonitoringLocationTypeName",
    "huc8": "HUCEightDigitCode",
    "lat": "LatitudeMeasure",
    "lon": "LongitudeMeasure",
    "aquifer": "AquiferName",
    "aquifer_type": "AquiferTypeName",
    "well_depth_ft": "WellDepthMeasure/MeasureValue",
    "well_depth_unit": "WellDepthMeasure/MeasureUnitCode",
}


class Log:
    def __init__(self):
        self.rows = []

    def step(self, name, rule, before, after):
        self.rows.append({"step": name, "rule": rule, "rows_before": int(before),
                          "rows_after": int(after), "rows_removed": int(before - after)})

    def frame(self):
        return pd.DataFrame(self.rows)


def load_raw() -> tuple[pd.DataFrame, pd.DataFrame]:
    res = pd.read_csv(RAW / "wqp_result.csv", dtype=str, keep_default_na=False)
    res.insert(0, "raw_row", np.arange(2, len(res) + 2))  # 1-based line number in the CSV
    st = pd.read_csv(RAW / "wqp_station.csv", dtype=str, keep_default_na=False)
    return res, st


def canonicalize(df: pd.DataFrame) -> pd.DataFrame:
    """Rename, parse numbers, map parameter codes, convert units, build censoring bounds."""
    d = df[["raw_row"] + list(COLS.values())].rename(columns={v: k for k, v in COLS.items()})
    d["date"] = pd.to_datetime(d["date"], format="%Y-%m-%d")
    d["year"] = d["date"].dt.year
    fam = d["pcode"].map(lambda p: PCODE.get(p, ("unmapped", "", "unmapped")))
    d["family"] = fam.map(lambda t: t[0])
    d["pcode_role"] = fam.map(lambda t: t[2])
    d["fraction_expected"] = fam.map(lambda t: t[1])
    d["value_num"] = pd.to_numeric(d["value_raw"].replace("", np.nan))
    d["dl_num"] = pd.to_numeric(d["dl_raw"].replace("", np.nan))
    d["censored"] = d["detect_cond"].isin(["Not Detected", "Detected Not Quantified"])
    d["dnq"] = d["detect_cond"] == "Detected Not Quantified"
    d["estimated"] = d["value_type"] == "Estimated"

    # Unit conversion. Detected rows carry the unit on the result; censored rows
    # carry it on the detection-limit field. Unknown units raise.
    def conv(row, which):
        if which == "value":
            v, u = row["value_num"], row["unit_raw"]
        else:
            v, u = row["dl_num"], row["dl_unit_raw"]
        if pd.isna(v):
            return np.nan
        if row["family"] == "unmapped":
            return np.nan
        return v * factor_to_canonical(u, row["family"])

    d["value"] = d.apply(conv, axis=1, which="value")
    d["dl"] = d.apply(conv, axis=1, which="dl")
    d["unit"] = d["family"].map(CANONICAL_UNIT)
    # Censoring interval
    d["lower"] = np.where(d["censored"], 0.0, d["value"])
    d["upper"] = np.where(d["censored"], d["dl"], d["value"])
    d["dl_missing"] = d["dl"].isna()
    return d


def prepare(res: pd.DataFrame, st: pd.DataFrame, write: bool = True) -> dict:
    """Run every preparation step on the raw result and station tables."""
    log = Log()
    n0 = len(res)

    # 1. Medium: groundwater only. The query asked for wells, but the portal also
    #    returns leachate, soil-moisture and other matrices collected at well sites.
    gw = res[(res["ActivityMediaName"] == "Water") & (res["ActivityMediaSubdivisionName"] == "Groundwater")]
    log.step("medium", "ActivityMediaName == 'Water' and ActivityMediaSubdivisionName == 'Groundwater'", n0, len(gw))
    media_removed = res.loc[~res.index.isin(gw.index), "ActivityMediaSubdivisionName"].value_counts().to_dict()

    # 2. Activity type: routine field samples for analysis; field replicates kept
    #    separately for precision; everything else excluded.
    routine = gw[gw["ActivityTypeCode"] == "Sample-Routine"]
    reps = gw[gw["ActivityTypeCode"] == "Quality Control Sample-Field Replicate"]
    other = gw[~gw.index.isin(routine.index) & ~gw.index.isin(reps.index)]
    log.step("activity_type", "ActivityTypeCode == 'Sample-Routine' (replicates kept separately)", len(gw), len(routine))
    activity_removed = other["ActivityTypeCode"].value_counts().to_dict()

    clean = canonicalize(routine)
    reps_c = canonicalize(reps)

    # 3. Parameter-code mapping checks
    assert (clean["family"] != "unmapped").all(), clean.loc[clean["family"] == "unmapped", "pcode"].unique()
    frac_mismatch = clean[clean["fraction"] != clean["fraction_expected"]]
    assert len(frac_mismatch) == 0, frac_mismatch[["pcode", "fraction"]].drop_duplicates()

    # 4. Derived duplicates: 71851 (nitrate as NO3) is computed by NWIS from 00618
    #    (nitrate as N). Verify the ratio on paired activities, then drop the derived rows.
    pv = clean.pivot_table(index="activity_id", columns="pcode", values="value_num", aggfunc="first")
    ratio_check = {}
    for derived, source in [("71851", "00618"), ("71850", "00620")]:
        if derived in pv and source in pv:
            pair = pv[[derived, source]].dropna()
            ratio = pair[derived] / pair[source]
            ratio_check[f"{derived}/{source}"] = {
                "n_pairs": int(len(pair)),
                "expected": round(1 / NO3_TO_N, 4),
                "ratio_min": round(float(ratio.min()), 4),
                "ratio_max": round(float(ratio.max()), 4),
            }
            # Derived values are reported to 2 significant figures, so the ratio
            # can deviate from 4.4265 by a few percent (e.g. 2.6 mg/L as N -> 11 or 12 as NO3).
            rel = (ratio * NO3_TO_N - 1).abs()
            assert rel.max() < 0.06, "derived nitrate rows do not match source rows within 6%"
    n_before = len(clean)
    clean = clean[clean["pcode_role"] != "derived_duplicate"]
    log.step("derived_duplicates", "drop USGS pcodes 71851/71850: NWIS-computed re-expression of 00618/00620 in NO3 units", n_before, len(clean))

    # 5. Key uniqueness: one row per activity and parameter code.
    dup = clean.duplicated(["activity_id", "pcode"], keep=False)
    assert not dup.any(), clean.loc[dup, ["activity_id", "pcode"]]
    # Multiple routine activities for the same well on the same day are kept and flagged.
    same_day = clean.groupby(["site_id", "date", "pcode"])["activity_id"].transform("nunique")
    clean["same_day_activities"] = same_day

    # 6. Station join: must not change the row count.
    stc = st[list(STATION_COLS.values())].rename(columns={v: k for k, v in STATION_COLS.items()})
    assert stc["site_id"].is_unique
    n_before = len(clean)
    clean = clean.merge(stc, on="site_id", how="left", validate="many_to_one")
    assert len(clean) == n_before
    reps_c = reps_c.merge(stc, on="site_id", how="left", validate="many_to_one")
    unmatched_sites = int(clean["site_name"].isna().sum())

    # 7. Analysis subset: dissolved fraction, primary parameter codes.
    n_before = len(clean)
    analysis = clean[clean["pcode_role"] == "primary"].copy()
    log.step("analysis_subset", "keep primary pcodes (01000 arsenic dissolved, 00618 nitrate as N dissolved, 00631 NO3+NO2 as N dissolved); other fractions kept in results_clean only", n_before, len(analysis))

    # Sanity: every censored row has a limit and every detected row has a value.
    assert analysis.loc[analysis["censored"], "dl"].notna().all(), "censored row without a limit"
    assert analysis.loc[~analysis["censored"], "value"].notna().all(), "detected row without a value"

    summary = {
        "raw_rows": int(n0),
        "media_removed": media_removed,
        "activity_type_removed": activity_removed,
        "replicate_rows": int(len(reps_c)),
        "derived_duplicate_ratio_check": ratio_check,
        "unmatched_station_rows": unmatched_sites,
        "results_clean_rows": int(len(clean)),
        "analysis_rows": int(len(analysis)),
        "analysis_by_family": analysis.groupby("family").agg(
            rows=("raw_row", "size"), wells=("site_id", "nunique"),
            censored=("censored", "sum"), estimated=("estimated", "sum"),
            dl_missing=("dl_missing", "sum"), first=("date", "min"), last=("date", "max"),
        ).assign(first=lambda d: d["first"].dt.date.astype(str), last=lambda d: d["last"].dt.date.astype(str)).to_dict("index"),
        "status_counts": analysis["status"].value_counts().to_dict(),
    }
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        clean.to_csv(OUT / "results_clean.csv", index=False)
        analysis.to_csv(OUT / "analysis_samples.csv", index=False)
        reps_c.to_csv(OUT / "replicates.csv", index=False)
        log.frame().to_csv(OUT / "exclusion_log.csv", index=False)
        (OUT / "prepare_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    return {"clean": clean, "analysis": analysis, "replicates": reps_c, "log": log.frame(), "summary": summary}


if __name__ == "__main__":
    out = prepare(*load_raw())
    print(out["log"].to_string(index=False))
    print(json.dumps(out["summary"], indent=2, default=str))
