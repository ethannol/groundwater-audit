"""Hand-checkable tests of the reference calculations in gwaudit.analysis."""
import numpy as np
import pandas as pd
import pytest

from gwaudit import analysis as A


def cohort_frame(pairs):
    """pairs: list of (site, early_lower, early_upper, late_lower, late_upper)."""
    rows = []
    for s, el, eu, ll, lu in pairs:
        rows.append({"site_id": s, "period": "early", "lower": el, "upper": eu, "date": pd.Timestamp("2005-01-01")})
        rows.append({"site_id": s, "period": "late", "lower": ll, "upper": lu, "date": pd.Timestamp("2015-01-01")})
    return pd.DataFrame(rows)


def test_paired_change_counts_and_sign_test():
    pairs = [("a", 5, 5, 3, 3), ("b", 5, 5, 4, 4), ("c", 5, 5, 6, 6), ("d", 0, 2, 1, 1), ("e", 0, 2, 9, 9)]
    res, p = A.paired_change(cohort_frame(pairs))
    # a, b decline; c increase; d: ND<2 then 1 -> indeterminate; e: ND<2 then 9 -> increase
    assert (res["decline"], res["increase"], res["indeterminate"]) == (2, 2, 1)
    assert res["sign_test"]["determinate"] == 4
    assert res["sign_test"]["declines_among_determinate"] == 2
    assert res["sign_test"]["p_two_sided"] == 1.0
    assert res["median_years_apart"] == pytest.approx(10.0, abs=0.01)
    assert res["both_detected"] == 3


def test_substitution_sensitivity_is_reported_separately():
    pairs = [("a", 0, 2, 0.9, 0.9), ("b", 0, 2, 0.9, 0.9), ("c", 0, 2, 0.9, 0.9)]
    res, _ = A.paired_change(cohort_frame(pairs))
    # interval logic: all indeterminate (0.9 lies inside [0, 2]); substitution makes the
    # direction depend on the substituted value: half (1.0 -> 0.9) says decline, zero (0 -> 0.9) says increase
    assert res["decline"] == 0 and res["indeterminate"] == 3
    assert res["substitution_sensitivity"]["half"]["share_declining"] == 1.0
    assert res["substitution_sensitivity"]["limit"]["share_declining"] == 1.0
    assert res["substitution_sensitivity"]["zero"]["share_declining"] == 0.0


def test_censored_summary_threshold_share_identifiability():
    s = A.censored_summary([0, 0, 12, 3], [2, 2, 12, 3], threshold=10)
    assert s["above_threshold_share"] == 0.25
    s2 = A.censored_summary([0, 12, 3], [20, 12, 3], threshold=10)  # ND <20 straddles 10
    assert s2["above_threshold_share"] is None and s2["above_threshold_undetermined"] == 1


def test_pooled_vs_cohort_detects_composition_change():
    rows = []
    for i in range(10):  # ten high wells sampled in both periods, unchanged
        for p, y in [("early", 2005), ("late", 2015)]:
            rows.append({"site_id": f"h{i}", "period": p, "year": y, "date": pd.Timestamp(f"{y}-01-01"), "lower": 8.0, "upper": 8.0})
    for i in range(30):  # thirty low wells only in the late period
        rows.append({"site_id": f"l{i}", "period": "late", "year": 2015, "date": pd.Timestamp("2015-01-01"), "lower": 1.0, "upper": 1.0})
    d = pd.DataFrame(rows)
    res, coh = A.pooled_vs_cohort(d, "nitrate_as_n")
    assert res["pooled_early"]["km_median"] == 8.0
    assert res["pooled_late"]["km_median"] == 1.0
    assert res["cohort_wells"] == 10 and res["wells_only_late"] == 30
    assert res["cohort_early"]["km_median"] == 8.0 and res["cohort_late"]["km_median"] == 8.0
    pc, _ = A.paired_change(coh)
    assert pc["decline"] == 0 and pc["increase"] == 0 and pc["indeterminate"] == 10


def test_last_sample_per_well_period_is_used():
    d = pd.DataFrame([
        {"site_id": "a", "period": "early", "date": pd.Timestamp("2004-01-01"), "lower": 1, "upper": 1},
        {"site_id": "a", "period": "early", "date": pd.Timestamp("2009-01-01"), "lower": 5, "upper": 5},
    ])
    one = A.last_per_well_period(d)
    assert len(one) == 1 and one.iloc[0]["lower"] == 5


def test_per_well_kendall_hand_case():
    d = pd.DataFrame([{"site_id": "w", "date": pd.Timestamp(f"20{y:02d}-01-01"), "lower": v, "upper": v, "censored": False}
                      for y, v in zip(range(10, 16), [6, 5, 4, 3, 2, 1])])
    kt = A.per_well_kendall(d, min_n=6)
    assert kt.iloc[0]["kendall_S"] == -15 and kt.iloc[0]["tau"] == -1.0
