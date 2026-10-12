"""Build a presentation ledger from the unchanged analysis and published scores.

No analysis or model calls; historical evaluation remains the claim baseline.
"""

from __future__ import annotations

import json
from pathlib import Path


def build(root: Path) -> dict:
    result = json.loads((root / "reports/results.json").read_text())
    scores = [
        json.loads(p.read_text())["summary"]
        for p in sorted(root.glob("eval/runs/T*_*_r*/score.json"))
    ]
    if not scores:
        raise ValueError("published evaluation scores are missing")
    costs = {
        condition: sum(s["cost_usd"] for s in scores if s["condition"] == condition)
        for condition in ["A", "B"]
    }
    result["evaluation"] = {
        "runs": len(scores),
        "checks": sum(s["checks"] for s in scores),
        "passed": sum(s["passed"] for s in scores),
        "critical_failures": sum(s["critical_failures"] for s in scores),
        "total_cost_usd": round(sum(costs.values()), 2),
        "workflow_cost_uplift_pct": 100 * (costs["B"] / costs["A"] - 1),
        "baseline": "Published original scores; scorer v2 is a separate exploratory re-score",
        "sources": [
            str(p.relative_to(root))
            for p in sorted(root.glob("eval/runs/T*_*_r*/score.json"))
        ],
    }
    return result


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    output = root / "reports/presentation.json"
    output.write_text(json.dumps(build(root), indent=2) + "\n")
    print(f"wrote {output}")
