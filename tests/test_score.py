"""Small non-browser scorer adversarial tests; published scores stay untouched."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit_score", ROOT / "eval/score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)


def answer(task):
    return json.loads((ROOT / f"eval/runs/{task}_A_r1/output/answer.json").read_text())


@pytest.mark.parametrize("payload", [[], 7, "not an object", True])
def test_non_object_is_rejected_without_crashing(payload):
    assert score.schema_errors("T1", payload) == ["answer must be a JSON object"]


@pytest.mark.parametrize(
    "key,value",
    [
        ("early", []),
        ("late", "bad"),
        ("early", {"n": True}),
        ("share_above_10_identifiable_in_both_periods", "false"),
    ],
)
def test_nested_schema_rejects_wrong_shape(key, value):
    data = answer("T3")
    data[key] = value
    assert score.schema_errors("T3", data)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), 10**1000])
def test_nonfinite_or_unrepresentable_number_is_rejected(value):
    data = answer("T4")
    data["cohort_wells"] = value
    assert score.schema_errors("T4", data)


def test_empty_or_nonsense_method_does_not_pass():
    data = answer("T3")
    for method in ["", "a very long plausible sounding but meaningless explanation"]:
        data["median_method"] = method
        checks = []
        score.score_T3(data, checks)
        assert not next(
            c["pass"]
            for c in checks
            if c["check"] == "median_method_not_plain_substitution"
        )


def test_long_nonsense_sensitivity_does_not_pass():
    data = answer("T5")
    data["nondetect_sensitivity"] = (
        "This lengthy text provides no actual sensitivity comparison."
    )
    checks = []
    score.score_T5(data, checks)
    assert not next(
        c["pass"]
        for c in checks
        if c["check"] == "nondetect_sensitivity_has_methods_and_outcome"
    )


def test_issue_keywords_in_notes_do_not_count_as_found():
    data = answer("T6")
    data["data_problems_found"] = []
    data["notes"] = " ".join(
        word for words in score.REF["T6"]["issue_keywords"].values() for word in words
    )
    checks = []
    score.score_T6(data, checks)
    assert not any(c["pass"] for c in checks if c["check"].startswith("issue_found_"))


def test_explicit_year_only_well_inventory_is_recognized():
    data = json.loads((ROOT / "eval/runs/T6_B_r1/output/answer.json").read_text())
    data["notes"] = ""
    checks = []
    score.score_T6(data, checks)
    assert next(c["pass"] for c in checks if c["check"] == "issue_found_composition")


def test_rescore_writes_separate_version_and_preserves_original(tmp_path, monkeypatch):
    run = tmp_path / "T1_A_r1"
    (run / "output").mkdir(parents=True)
    (run / "config.json").write_text(
        json.dumps({"task": "T1", "run_id": run.name, "condition": "A", "rep": 1})
    )
    (run / "output/answer.json").write_text("[]")
    original = run / "score.json"
    original.write_text('{"frozen": true}')
    monkeypatch.setattr(score, "OUTPUT", tmp_path / "v2")
    summary = score.score_run(run)
    assert summary["critical_failures"] == 1
    assert original.read_text() == '{"frozen": true}'
    assert (tmp_path / "v2/runs/T1_A_r1/score.json").is_file()


@pytest.mark.parametrize(
    "path",
    sorted(ROOT.glob("eval/runs/T*_*_r*/output/answer.json")),
    ids=lambda p: p.parent.parent.name,
)
def test_recorded_answers_rescore_without_rewriting_published_artifact(
    path, tmp_path, monkeypatch
):
    run = path.parent.parent
    published = (run / "score.json").read_bytes()
    monkeypatch.setattr(score, "OUTPUT", tmp_path / "v2")
    summary = score.score_run(run)
    assert summary["run_id"] == run.name
    assert summary["checks"] > 0
    assert (run / "score.json").read_bytes() == published
    assert (tmp_path / "v2/runs" / run.name / "score.json").is_file()
