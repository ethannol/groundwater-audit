"""Generic checks for Water Quality Portal style tables (Condition B helper).

These functions make no assumptions about the constituents or the expected
answers; they only surface structure the analyst must then interpret.

    from validators import *
    df = pd.read_csv("data/wqp_result.csv", dtype=str, keep_default_na=False)
    tabulate_fields(df)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_FIELDS = [
    "ActivityMediaName", "ActivityMediaSubdivisionName", "ActivityTypeCode",
    "CharacteristicName", "USGSPCode", "ResultSampleFractionText",
    "ResultMeasure/MeasureUnitCode", "DetectionQuantitationLimitMeasure/MeasureUnitCode",
    "ResultDetectionConditionText", "ResultValueTypeName", "ResultStatusIdentifier",
    "ResultAnalyticalMethod/MethodIdentifier", "LaboratoryName",
]


def tabulate_fields(df: pd.DataFrame, fields=None, top: int = 12) -> dict:
    """Value counts for the categorical fields an analysis depends on."""
    out = {}
    for f in fields or DEFAULT_FIELDS:
        if f in df.columns:
            out[f] = df[f].value_counts(dropna=False).head(top).to_dict()
    for f, counts in out.items():
        print(f"--- {f}")
        for k, v in counts.items():
            print(f"    {k!r}: {v}")
    return out


def check_unique_key(df: pd.DataFrame, key: list[str]) -> dict:
    """How many rows share a key that is supposed to be unique."""
    dup = df.duplicated(key, keep=False)
    out = {"key": key, "rows": int(len(df)), "duplicated_rows": int(dup.sum()),
           "example": df.loc[dup, key].head(5).to_dict("records")}
    print(out)
    return out


def check_reexpressed_pairs(df: pd.DataFrame, group_key: list[str], code_col: str = "USGSPCode",
                            value_col: str = "ResultMeasureValue") -> pd.DataFrame:
    """Within each group (for example one sampling activity), compare pairs of
    parameter codes whose values are a near-constant multiple of each other.
    A constant ratio across many groups suggests the same measurement reported
    twice in different units."""
    v = df.assign(_v=pd.to_numeric(df[value_col].replace("", np.nan)))
    pv = v.pivot_table(index=group_key, columns=code_col, values="_v", aggfunc="first")
    rows = []
    codes = list(pv.columns)
    for i, a in enumerate(codes):
        for b in codes[i + 1:]:
            pair = pv[[a, b]].dropna()
            if len(pair) < 10:
                continue
            ratio = pair[b] / pair[a]
            ratio = ratio[np.isfinite(ratio)]
            if len(ratio) and ratio.std() / max(abs(ratio.mean()), 1e-9) < 0.05:
                rows.append({"code_a": a, "code_b": b, "n_pairs": len(pair),
                             "ratio_b_over_a_mean": round(float(ratio.mean()), 4),
                             "ratio_cv": round(float(ratio.std() / abs(ratio.mean())), 4)})
    out = pd.DataFrame(rows)
    print(out.to_string(index=False) if len(out) else "no near-constant-ratio pairs found")
    return out


def censoring_profile(df: pd.DataFrame, by=("CharacteristicName",), year_col="ActivityStartDate",
                      cond_col="ResultDetectionConditionText",
                      dl_col="DetectionQuantitationLimitMeasure/MeasureValue") -> pd.DataFrame:
    """Censored share and reporting-limit summary by group and year."""
    d = df.copy()
    d["_year"] = d[year_col].astype(str).str[:4]
    d["_cens"] = d[cond_col].astype(str) != ""
    d["_dl"] = pd.to_numeric(d[dl_col].replace("", np.nan))
    g = d.groupby(list(by) + ["_year"]).agg(n=("_cens", "size"), censored=("_cens", "sum"),
                                             dl_min=("_dl", "min"), dl_median=("_dl", "median"), dl_max=("_dl", "max"))
    g["censored_share"] = (g["censored"] / g["n"]).round(3)
    print(g.to_string())
    return g.reset_index()


def cohort_composition(df: pd.DataFrame, site_col: str, period_col: str) -> dict:
    """Which sites appear in each period, and how many appear in all of them."""
    sets = {p: set(s) for p, s in df.groupby(period_col)[site_col]}
    common = set.intersection(*sets.values()) if sets else set()
    out = {"sites_per_period": {p: len(s) for p, s in sets.items()},
           "sites_in_all_periods": len(common),
           "sites_in_only_one_period": sum(1 for s in set.union(*sets.values()) if sum(s in v for v in sets.values()) == 1) if sets else 0}
    print(out)
    return out
