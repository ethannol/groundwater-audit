"""Invariance checks: the reference pipeline on fixtures with known properties.

Every fixture is synthetic (eval/fixtures/make_fixtures.py) and carries a
truth.json. These tests pin the pipeline's behaviour to that truth.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from gwaudit import analysis as A
from gwaudit import prepare as P
from gwaudit.units import UnitError

FX = Path(__file__).resolve().parents[1] / "eval" / "fixtures"


def load(name):
    d = FX / name
    res = pd.read_csv(d / "wqp_result.csv", dtype=str, keep_default_na=False)
    res.insert(0, "raw_row", np.arange(2, len(res) + 2))
    st = pd.read_csv(d / "wqp_station.csv", dtype=str, keep_default_na=False)
    truth = json.loads((d / "truth.json").read_text())
    assert truth["synthetic"] is True and (res["SYNTHETIC"] == "1").all()
    return res, st, truth


def run_pipeline(res, st):
    out = P.prepare(res, st, write=False)
    d = out["analysis"].copy()
    d["period"] = A.period_of(d["year"])
    pvc, coh = A.pooled_vs_cohort(d, "nitrate_as_n")
    pc, pairs = A.paired_change(coh)
    return out, pvc, pc, pairs


def test_clean_fixture_recovers_the_planted_decline():
    res, st, truth = load("clean")
    out, pvc, pc, pairs = run_pipeline(res, st)
    e = truth["expected"]
    assert len(out["analysis"]) == e["rows_after_preparation"]
    assert pvc["cohort_wells"] == e["cohort_wells"]
    assert (pc["decline"], pc["increase"], pc["indeterminate"]) == (e["decline"], e["increase"], e["indeterminate"])
    assert pc["wilcoxon_both_detected"]["median_ratio_late_over_early"] == pytest.approx(e["median_ratio_late_over_early"], abs=0.01)


def test_unit_mix_fixture_is_not_double_counted():
    res, st, truth = load("unit_mix")
    out, pvc, pc, pairs = run_pipeline(res, st)
    e = truth["expected"]
    assert len(res) == e["naive_row_count_if_not_deduplicated"]
    assert len(out["analysis"]) == e["rows_after_preparation"]
    assert pc["decline"] == e["decline"]
    assert pc["wilcoxon_both_detected"]["median_ratio_late_over_early"] == pytest.approx(0.7, abs=0.01)


def test_dup_key_fixture_is_refused_by_the_join():
    res, st, truth = load("dup_key")
    with pytest.raises(AssertionError):
        P.prepare(res, st, write=False)
    # a naive merge would multiply rows
    naive = res.merge(st, on="MonitoringLocationIdentifier", how="left")
    assert len(naive) == truth["expected"]["rows_if_join_multiplies"]


def test_dl_change_fixture_yields_no_spurious_decline():
    res, st, truth = load("dl_change")
    out, pvc, pc, pairs = run_pipeline(res, st)
    e = truth["expected"]
    assert pc["decline"] == 0 and pc["increase"] == 0
    assert pc["indeterminate"] >= e["indeterminate_at_least"]
    # the substitution sensitivity makes the spurious decline visible as a method artefact
    assert pc["substitution_sensitivity"]["half"]["share_declining"] > 0.8


def test_composition_fixture_separates_pooled_from_cohort():
    res, st, truth = load("composition")
    out, pvc, pc, pairs = run_pipeline(res, st)
    e = truth["expected"]
    assert pvc["pooled_early"]["km_median"] == pytest.approx(e["pooled_median_early_about"], abs=0.05)
    assert pvc["pooled_late"]["km_median"] == pytest.approx(e["pooled_median_late_about"], abs=0.05)
    assert pvc["pooled_late"]["km_median"] < pvc["pooled_early"]["km_median"]
    assert pvc["cohort_wells"] == e["cohort_wells"]
    assert (pc["decline"], pc["increase"]) == (0, 0)


def test_missing_units_fixture_raises():
    res, st, truth = load("missing_units")
    with pytest.raises(UnitError):
        P.prepare(res, st, write=False)
    assert (res["ResultMeasure/MeasureUnitCode"] == "").sum() == truth["expected"]["rows_with_missing_unit"]
