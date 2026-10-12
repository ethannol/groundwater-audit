"""Presentation claims are derived from original published score artifacts."""

import json
from pathlib import Path

from gwaudit.presentation import build


def test_presentation_preserves_reference_and_derives_secondary_numbers():
    root = Path(__file__).resolve().parents[1]
    original = json.loads((root / "reports/results.json").read_text())
    presentation = build(root)
    evaluation = presentation.pop("evaluation")
    assert presentation == original
    assert evaluation["runs"] == 24
    assert evaluation["checks"] == 272
    assert evaluation["passed"] == 267
    assert evaluation["critical_failures"] == 0
    assert evaluation["total_cost_usd"] == 4.33
    scores = [
        json.loads(p.read_text())["summary"]
        for p in root.glob("eval/runs/T*_*_r*/score.json")
    ]
    a_cost = sum(s["cost_usd"] for s in scores if s["condition"] == "A")
    b_cost = sum(s["cost_usd"] for s in scores if s["condition"] == "B")
    assert evaluation["workflow_cost_uplift_pct"] == 100 * (b_cost / a_cost - 1)
