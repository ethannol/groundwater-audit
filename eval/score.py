"""Score recorded evaluation runs against the reference answers.

    python eval/score.py            # scores every run under eval/runs/ with an answer.json
    python eval/score.py --table    # writes eval/scoring/v2.1/results.md

Version 2 is an exploratory re-score. Original score.json, scores.csv and
eval/results.md are retained unchanged and continue to support published claims.

Numerical checks are mechanical (eval/scoring/reference.json, tolerances
below). Interpretive scoring lives in eval/scoring/interpretive.csv, filled in
by a human reader with the rubric in eval/scoring/RUBRIC.md; this script only
merges it. A run with no answer.json scores zero numerical checks and is
listed, never dropped.

Severity: 'critical' = a wrong value or claim that changes the conclusion;
'major' = a wrong number that a reviewer would need to correct; 'minor' =
cosmetic or ambiguous.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "eval"
SCORER_VERSION = "v2.1-schema-review"
OUTPUT = EVAL / "scoring" / "v2.1"
REF = json.loads((EVAL / "scoring" / "reference.json").read_text())


def num(x):
    try:
        value = float(x)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError, OverflowError):
        return None


def close(x, ref, abs_tol=0.0, rel_tol=0.0):
    x = num(x)
    if x is None or ref is None:
        return False
    return abs(x - ref) <= max(abs_tol, rel_tol * abs(ref))


def check(checks, name, ok, severity, got, want):
    checks.append(
        {
            "check": name,
            "pass": bool(ok),
            "severity": severity,
            "got": got,
            "want": want,
        }
    )


def score_T1(a, c):
    r = REF["T1"]
    for k in ["rows_total", "rows_groundwater", "rows_routine_groundwater"]:
        check(c, k, close(a.get(k), r[k]), "major", a.get(k), r[k])
    check(
        c,
        "rows_qc_groundwater",
        num(a.get("rows_qc_groundwater"))
        in [
            r["rows_qc_groundwater"]["value"],
            *r["rows_qc_groundwater"]["also_accept"],
        ],
        "minor",
        a.get("rows_qc_groundwater"),
        r["rows_qc_groundwater"],
    )
    got = a.get("non_groundwater_media") or {}
    check(
        c,
        "non_groundwater_media",
        isinstance(got, dict)
        and all(close(got.get(k), v) for k, v in r["non_groundwater_media"].items()),
        "major",
        got,
        r["non_groundwater_media"],
    )
    for k in [
        "arsenic_dissolved_routine_rows",
        "arsenic_dissolved_routine_wells",
        "arsenic_nondetect_rows",
    ]:
        check(c, k, close(a.get(k), r[k]), "major", a.get(k), r[k])
    # 521 counts distinct activities, 490 distinct sampling dates; the task did not say which (see docs/decisions.md)
    k = "arsenic_wells_with_2plus_samples"
    check(
        c,
        k,
        num(a.get(k)) in [r[k], r["arsenic_wells_with_2plus_dates"]],
        "major",
        a.get(k),
        [r[k], r["arsenic_wells_with_2plus_dates"]],
    )
    for k in ["arsenic_first_year", "arsenic_last_year"]:
        check(c, k, close(a.get(k), r[k]), "minor", a.get(k), r[k])
    rl = a.get("arsenic_nondetect_limit_range_ugL") or [None, None]
    check(
        c,
        "arsenic_nondetect_limit_range_ugL",
        isinstance(rl, list)
        and len(rl) == 2
        and close(rl[0], r["arsenic_nondetect_limit_range_ugL"][0], 0.011)
        and close(rl[1], r["arsenic_nondetect_limit_range_ugL"][1], 0.011),
        "major",
        rl,
        r["arsenic_nondetect_limit_range_ugL"],
    )
    fields = " ".join(map(str, a.get("fields_with_material_missingness") or []))
    check(
        c,
        "flags_missing_limits_or_time",
        bool(re.search(r"Detection|Limit|Time", fields)),
        "minor",
        fields[:80],
        "mentions limit or time fields",
    )


def score_T2(a, c):
    r = REF["T2"]
    check(
        c,
        "rows_in_table",
        close(a.get("rows_in_table"), r["rows_in_table"]),
        "critical",
        a.get("rows_in_table"),
        r["rows_in_table"],
    )
    check(
        c,
        "wells_in_table",
        close(a.get("wells_in_table"), r["wells_in_table"]),
        "major",
        a.get("wells_in_table"),
        r["wells_in_table"],
    )
    check(
        c,
        "nondetect_rows_in_table",
        close(a.get("nondetect_rows_in_table"), r["nondetect_rows_in_table"]),
        "major",
        a.get("nondetect_rows_in_table"),
        r["nondetect_rows_in_table"],
    )
    inc = [str(p).zfill(5) for p in (a.get("pcodes_included") or [])]
    # The row count is the critical check (double counting shows up there); the code list is reporting.
    check(c, "pcodes_included_only_00618", inc == ["00618"], "major", inc, ["00618"])
    exc = {str(k).zfill(5): v for k, v in (a.get("pcodes_excluded") or {}).items()}
    text71851 = str(exc.get("71851", "")) + " " + str(a.get("notes", ""))
    check(
        c,
        "71851_treated_as_reexpression",
        "71851" in text71851
        and bool(
            re.search(
                r"same|re-?express|duplicate|convert|derived|NO3", text71851, re.IGNORECASE
            )
        ),
        "critical",
        text71851[:100],
        "71851 identified as a re-expression of 00618 (in pcodes_excluded or notes)",
    )
    check(
        c,
        "excludes_00631_different_definition",
        "00631" in exc,
        "major",
        exc.get("00631"),
        "00631 excluded (nitrate+nitrite)",
    )
    got = a.get("rows_dropped_as_same_measurement_reexpressed")
    check(
        c,
        "rows_dropped_as_same_measurement_reexpressed",
        num(got)
        in [
            r["rows_dropped_as_same_measurement_reexpressed"],
            r["rows_dropped_as_same_measurement_reexpressed_incl_total"],
        ],
        "minor",
        got,
        [
            r["rows_dropped_as_same_measurement_reexpressed"],
            r["rows_dropped_as_same_measurement_reexpressed_incl_total"],
        ],
    )
    got = a.get("rows_excluded_other_fraction")
    check(
        c,
        "rows_excluded_other_fraction",
        num(got)
        in [
            r["rows_excluded_other_fraction"],
            r["rows_excluded_other_fraction_incl_no3_units"],
        ],
        "minor",
        got,
        [
            r["rows_excluded_other_fraction"],
            r["rows_excluded_other_fraction_incl_no3_units"],
        ],
    )
    check(
        c,
        "nitrate_plus_nitrite_not_combined",
        a.get("nitrate_plus_nitrite_combined") is False,
        "major",
        a.get("nitrate_plus_nitrite_combined"),
        False,
    )
    factors = a.get("unit_conversion_factors_used") or {}
    fvals = [num(v) for v in factors.values()] if isinstance(factors, dict) else []
    check(
        c,
        "conversion_factor_if_used_is_0.226",
        (not fvals)
        or any(v is not None and abs(v - 0.2259) < 0.002 for v in fvals)
        or any(v is not None and abs(v - 1.0) < 1e-9 for v in fvals),
        "major",
        factors,
        "0.2259 for NO3->N (or none needed)",
    )


def score_T3(a, c):
    r = REF["T3"]
    for p in ["early", "late"]:
        g = a.get(p) or {}
        check(c, f"{p}_n", close(g.get("n"), r[p]["n"]), "major", g.get("n"), r[p]["n"])
        # 'Detected Not Quantified' rows (3, early) may be counted as non-detects or not; both readings accepted
        check(
            c,
            f"{p}_n_nondetect",
            close(g.get("n_nondetect"), r[p]["n_nondetect"], 3),
            "major",
            g.get("n_nondetect"),
            f"{r[p]['n_nondetect']} (±3 DNQ rows)",
        )
        check(
            c,
            f"{p}_reporting_limit_range",
            close(g.get("reporting_limit_min"), r[p]["reporting_limit_min"], 0.011)
            and close(g.get("reporting_limit_max"), r[p]["reporting_limit_max"], 0.011),
            "major",
            [g.get("reporting_limit_min"), g.get("reporting_limit_max")],
            [r[p]["reporting_limit_min"], r[p]["reporting_limit_max"]],
        )
        lo, hi = r[p]["median_accept_range"]
        m = num(g.get("median_ugL"))
        bounds_given = m is None and bool(
            re.search(
                r"bound",
                str(a.get("median_method", "")) + str(a.get("notes", "")),
                re.IGNORECASE,
            )
        )
        check(
            c,
            f"{p}_median",
            (m is not None and lo <= m <= hi) or bounds_given,
            "major",
            g.get("median_ugL"),
            f"{r[p]['median_ugL']} (accept {lo:.2f}-{hi:.2f}, or null with stated bounds)",
        )
    e = a.get("early") or {}
    check(
        c,
        "early_share_above_10",
        close(e.get("share_above_10_ugL"), r["early"]["share_above_10_ugL"], 0.005),
        "major",
        e.get("share_above_10_ugL"),
        r["early"]["share_above_10_ugL"],
    )
    l = a.get("late") or {}
    s = num(l.get("share_above_10_ugL"))
    b = r["late"]["share_above_10_ugL_bounds"]
    check(
        c,
        "late_share_above_10_within_bounds_or_null",
        s is None or (b[0] - 0.005 <= s <= b[1] + 0.005),
        "major",
        l.get("share_above_10_ugL"),
        f"null or within {b}",
    )
    mm = str(a.get("median_method", ""))
    named = re.search(r"bound|interval|Kaplan|\bKM\b|ROS|censor", mm, re.IGNORECASE)
    check(
        c,
        "median_method_not_plain_substitution",
        bool(named)
        and (
            not re.search(r"half|replace|substitut|set to", mm, re.IGNORECASE)
            or re.search(r"sensitiv|bound|interval|Kaplan|KM|ROS|censor", mm, re.IGNORECASE)
        ),
        "major",
        mm[:100],
        "censored estimator, bounds, or substitution with a stated sensitivity",
    )
    check(
        c,
        "identifiability_flag",
        a.get("share_above_10_identifiable_in_both_periods") is False,
        "minor",
        a.get("share_above_10_identifiable_in_both_periods"),
        False,
    )


def score_T4(a, c):
    r = REF["T4"]
    for p in ["pooled_early", "pooled_late"]:
        g = a.get(p) or {}
        check(c, f"{p}_n", close(g.get("n"), r[p]["n"]), "major", g.get("n"), r[p]["n"])
        check(
            c,
            f"{p}_wells",
            close(g.get("wells"), r[p]["wells"]),
            "major",
            g.get("wells"),
            r[p]["wells"],
        )
        check(
            c,
            f"{p}_median",
            close(g.get("median"), r[p]["median"], 0.06),
            "major",
            g.get("median"),
            r[p]["median"],
        )
    for k in ["cohort_wells", "wells_only_early", "wells_only_late"]:
        check(c, k, close(a.get(k), r[k]), "major", a.get(k), r[k])
    for k in ["cohort_early_median", "cohort_late_median"]:
        check(c, k, close(a.get(k), r[k], 0.06), "major", a.get(k), r[k])
    for k in ["cohort_decline", "cohort_increase", "cohort_indeterminate"]:
        check(c, k, close(a.get(k), r[k], 2), "major", a.get(k), r[k])
    v = str(a.get("did_nitrate_decline", "")).strip().lower()
    check(
        c,
        "did_nitrate_decline",
        v in r["did_nitrate_decline_accept"],
        "critical",
        v,
        r["did_nitrate_decline_accept"],
    )


def score_T5(a, c):
    r = REF["T5"]
    for k in ["cohort_wells", "decline", "increase", "indeterminate"]:
        check(c, k, close(a.get(k), r[k], 2), "major", a.get(k), r[k])
    den = str(a.get("share_declining_denominator", "")).lower()
    which = (
        "determinate wells"
        if "determin" in den and "all" not in den
        else "all cohort wells"
    )
    want = r["share_declining_by_denominator"][which]
    check(
        c,
        "share_declining_consistent_with_denominator",
        close(a.get("share_declining"), want["value"], 0.02),
        "major",
        f"{a.get('share_declining')} ({den})",
        f"{want['value']} for {which}",
    )
    ci = a.get("share_declining_ci95") or [None, None]
    check(
        c,
        "ci95_matches_denominator",
        isinstance(ci, list)
        and len(ci) == 2
        and close(ci[0], want["ci95"][0], 0.03)
        and close(ci[1], want["ci95"][1], 0.03),
        "major",
        ci,
        want["ci95"],
    )
    check(
        c,
        "sign_test_p",
        close(a.get("sign_test_p"), r["sign_test_p"], 0.02),
        "major",
        a.get("sign_test_p"),
        r["sign_test_p"],
    )
    check(
        c,
        "median_ratio_both_detected",
        close(
            a.get("median_ratio_late_over_early_both_detected"),
            r["median_ratio_late_over_early_both_detected"],
            0.015,
        ),
        "major",
        a.get("median_ratio_late_over_early_both_detected"),
        r["median_ratio_late_over_early_both_detected"],
    )
    iu = str(a.get("independent_unit", ""))
    check(
        c,
        "independent_unit_is_well",
        bool(re.search(r"\bwell", iu, re.IGNORECASE)),
        "critical",
        iu[:100],
        "the well",
    )
    ns = str(a.get("nondetect_sensitivity", ""))
    # Presence/structure can be checked mechanically; scientific correctness
    # remains an interpretive review, not a keyword-based correctness claim.
    methods = all(
        re.search(pattern, ns, re.IGNORECASE)
        for pattern in [r"zero|\b0\b", r"half|DL/2", r"full|limit"]
    )
    outcome = re.search(r"declin|increas|direction|[0-9]", ns, re.IGNORECASE)
    check(
        c,
        "nondetect_sensitivity_has_methods_and_outcome",
        bool(methods and outcome),
        "minor",
        ns[:80],
        "zero/half/full-limit methods and a stated outcome; requires review",
    )


def score_T6(a, c):
    r = REF["T6"]
    rec = str(a.get("recommendation", "")).strip().lower()
    check(
        c,
        "recommendation",
        rec in r["recommendation_accept"],
        "critical",
        rec,
        r["recommendation_accept"],
    )
    check(
        c,
        "cohort_wells",
        num(a.get("cohort_wells")) in r["cohort_wells_accept"],
        "major",
        a.get("cohort_wells"),
        r["cohort_wells_accept"],
    )
    check(
        c,
        "cohort_decline_zero",
        close(a.get("cohort_decline"), 0, 0),
        "critical",
        a.get("cohort_decline"),
        0,
    )
    check(
        c,
        "cohort_increase_zero",
        close(a.get("cohort_increase"), 0, 0),
        "major",
        a.get("cohort_increase"),
        0,
    )
    # Search the explicit issue inventory, not arbitrary notes where an issue
    # might be mentioned only to deny it. Human rubric review is still required.
    text = json.dumps(a.get("data_problems_found", [])).lower()
    found = {
        k: any(w in text for w in words) for k, words in r["issue_keywords"].items()
    }
    # "2018 only" and "only in 2018" describe the same well-set change.
    # Keep the inventory restriction without flagging a valid paraphrase.
    found["composition"] = found["composition"] or bool(
        re.search(r"\b(?:19|20)\d{2}[- ]+only\b", text)
    )
    for k, ok in found.items():
        check(c, f"issue_found_{k}", ok, "major", ok, True)


SCORERS = {
    "T1": score_T1,
    "T2": score_T2,
    "T3": score_T3,
    "T4": score_T4,
    "T5": score_T5,
    "T6": score_T6,
}


def schema_errors(task: str, answer) -> list[str]:
    """Check the requested answer shape before .get/nested/list operations.

    The frozen task specification supplies required keys. Unknown extra fields
    remain allowed; they belong to interpretive review rather than this schema.
    """
    if not isinstance(answer, dict):
        return ["answer must be a JSON object"]
    # Explicit keys from the frozen task specifications; do not infer JSON
    # structure from their illustrative, non-valid-JSON Markdown blocks.
    required = {
        "T1": """rows_total rows_groundwater rows_routine_groundwater rows_qc_groundwater
                 non_groundwater_media arsenic_dissolved_routine_rows
                 arsenic_dissolved_routine_wells arsenic_wells_with_2plus_samples
                 arsenic_nondetect_rows arsenic_first_year arsenic_last_year
                 arsenic_nondetect_limit_range_ugL fields_with_material_missingness notes""",
        "T2": """rows_in_table wells_in_table nondetect_rows_in_table pcodes_included
                 pcodes_excluded unit_conversion_factors_used
                 rows_dropped_as_same_measurement_reexpressed rows_excluded_other_fraction
                 nitrate_plus_nitrite_combined notes""",
        "T3": "early late median_method share_above_10_identifiable_in_both_periods notes",
        "T4": """pooled_early pooled_late cohort_wells wells_only_early wells_only_late
                 cohort_early_median cohort_late_median cohort_decline cohort_increase
                 cohort_indeterminate did_nitrate_decline notes""",
        "T5": """cohort_wells decline increase indeterminate share_declining
                 share_declining_denominator share_declining_ci95 ci_method sign_test_p
                 median_ratio_late_over_early_both_detected independent_unit
                 nondetect_sensitivity notes""",
        "T6": """recommendation cohort_wells cohort_decline cohort_increase cohort_indeterminate
                 pooled_median_early pooled_median_late data_problems_found
                 rows_affected_by_each_problem notes""",
    }[task].split()
    errors = [f"missing field {key}" for key in required if key not in answer]

    def numeric(value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False
        try:
            return math.isfinite(value)
        except OverflowError:
            return False

    string_fields = {
        "notes",
        "median_method",
        "did_nitrate_decline",
        "ci_method",
        "share_declining_denominator",
        "independent_unit",
        "nondetect_sensitivity",
        "recommendation",
    }
    dict_fields = {
        "non_groundwater_media",
        "pcodes_excluded",
        "unit_conversion_factors_used",
        "rows_affected_by_each_problem",
    }
    list_fields = {
        "fields_with_material_missingness",
        "pcodes_included",
        "data_problems_found",
    }
    pair_fields = {"arsenic_nondetect_limit_range_ugL", "share_declining_ci95"}
    bool_fields = {
        "nitrate_plus_nitrite_combined",
        "share_above_10_identifiable_in_both_periods",
    }
    nullable = {"sign_test_p", "median_ratio_late_over_early_both_detected"}
    for key in required:
        if key not in answer:
            continue
        value = answer[key]
        if key in string_fields:
            ok = isinstance(value, str)
        elif key in dict_fields:
            ok = isinstance(value, dict)
            if ok:
                ok = all(isinstance(k, str) for k in value)
                if key == "pcodes_excluded":
                    ok = ok and all(isinstance(v, str) for v in value.values())
                else:
                    ok = ok and all(numeric(v) and v >= 0 for v in value.values())
        elif key in list_fields:
            ok = isinstance(value, list) and all(
                isinstance(v, str)
                or (key == "pcodes_included" and numeric(v) and int(v) == v)
                for v in value
            )
        elif key in pair_fields:
            ok = (
                isinstance(value, list)
                and len(value) == 2
                and all(numeric(v) for v in value)
            )
        elif key in bool_fields:
            ok = isinstance(value, bool)
        elif key in {"early", "late", "pooled_early", "pooled_late"}:
            nested = (
                {
                    "n",
                    "n_nondetect",
                    "reporting_limit_min",
                    "reporting_limit_max",
                    "median_ugL",
                    "share_above_10_ugL",
                }
                if task == "T3"
                else {"n", "wells", "median"}
            )
            ok = isinstance(value, dict) and nested <= value.keys()
            if ok:
                ok = all(
                    numeric(value[k])
                    or (
                        task == "T3"
                        and value[k] is None
                        and k in {"median_ugL", "share_above_10_ugL"}
                    )
                    for k in nested
                )
        else:
            ok = numeric(value) or (key in nullable and value is None)
        if not ok:
            errors.append(f"invalid type/shape for {key}")
    return errors


def score_run(run_dir: Path) -> dict:
    cfg = json.loads((run_dir / "config.json").read_text())
    ans_path = run_dir / "output" / "answer.json"
    checks = []
    answer = None
    if ans_path.exists():
        try:
            answer = json.loads(ans_path.read_text())
        except json.JSONDecodeError as e:
            check(
                checks,
                "answer_json_parses",
                False,
                "critical",
                str(e)[:80],
                "valid JSON",
            )
    if answer is not None:
        errors = schema_errors(cfg["task"], answer)
        if errors:
            check(
                checks,
                "answer_schema_valid",
                False,
                "critical",
                errors,
                "task answer schema",
            )
        else:
            SCORERS[cfg["task"]](answer, checks)
    else:
        check(
            checks, "answer_json_present", False, "critical", "missing", "answer.json"
        )
    crit = [x for x in checks if x["severity"] == "critical" and not x["pass"]]
    maj = [x for x in checks if x["severity"] == "major" and not x["pass"]]
    out = {
        "scorer_version": SCORER_VERSION,
        "run_id": cfg["run_id"],
        "task": cfg["task"],
        "condition": cfg["condition"],
        "rep": cfg["rep"],
        "cost_usd": cfg.get("cost_usd"),
        "wall_seconds": cfg.get("wall_seconds"),
        "num_turns": cfg.get("num_turns"),
        "model_used": ",".join(cfg.get("model_used") or []),
        "answer_present": answer is not None,
        "checks": len(checks),
        "passed": sum(x["pass"] for x in checks),
        "critical_failures": len(crit),
        "major_failures": len(maj),
        "failed_checks": "; ".join(
            f"{x['check']} (got {x['got']}, want {x['want']})"
            for x in checks
            if not x["pass"]
        ),
    }
    destination = OUTPUT / "runs" / cfg["run_id"]
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "score.json").write_text(
        json.dumps({"summary": out, "checks": checks}, indent=2, default=str)
    )
    return out


def load_interpretive():
    p = EVAL / "scoring" / "interpretive.csv"
    if not p.exists():
        return {}
    with p.open() as f:
        return {r["run_id"]: r for r in csv.DictReader(f)}


def main(table: bool):
    runs = sorted(
        p
        for p in (EVAL / "runs").iterdir()
        if p.is_dir() and (p / "config.json").exists()
    )
    rows = [score_run(p) for p in runs]
    interp = load_interpretive()
    for r in rows:
        i = interp.get(r["run_id"], {})
        r.update(
            {
                "interp_unsupported_claims": i.get("unsupported_claims", ""),
                "interp_omitted_caveats": i.get("omitted_caveats", ""),
                "interp_justified_abstention": i.get("justified_abstention", ""),
                "interp_verdict": i.get("verdict", ""),
                "interp_notes": i.get("notes", ""),
                "needs_ethan_review": i.get("needs_ethan_review", "yes"),
            }
        )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / "scores.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["run_id"])
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(
            f"{r['run_id']:<14} cost ${r['cost_usd'] if r['cost_usd'] is not None else float('nan'):.2f}  {r['wall_seconds']:>7}s  "
            f"turns {r['num_turns']}  checks {r['passed']}/{r['checks']}  critical {r['critical_failures']}  major {r['major_failures']}"
        )
    if table:
        write_table(rows)


def write_table(rows):
    matrix = [r for r in rows if not r["run_id"].startswith("pilot")]
    lines = [
        f"# Evaluation results ({SCORER_VERSION}; exploratory re-score)",
        "",
        "Generated by `python eval/score.py --table` from recorded runs in `eval/runs/`. No run is omitted; pilot runs are listed separately.",
        "",
        "## Per-run results",
        "",
        "| Run | Task | Cond. | Rep | Model | Cost (USD) | Wall (s) | Turns | Numerical checks passed | Critical | Major | Interpretive verdict | Needs review |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in matrix:
        lines.append(
            f"| {r['run_id']} | {r['task']} | {r['condition']} | {r['rep']} | {r['model_used']} | {r['cost_usd']:.2f} | {r['wall_seconds']:.0f} | {r['num_turns']} | "
            f"{r['passed']}/{r['checks']} | {r['critical_failures']} | {r['major_failures']} | {r['interp_verdict']} | {r['needs_ethan_review']} |"
        )
    lines += [
        "",
        "## By condition",
        "",
        "| Condition | Runs | Mean cost (USD) | Mean wall (s) | Numerical checks passed | Runs with a critical failure | Major failures (total) |",
        "|---|---|---|---|---|---|---|",
    ]
    for cond in ["A", "B"]:
        g = [r for r in matrix if r["condition"] == cond]
        if not g:
            continue
        lines.append(
            f"| {cond} | {len(g)} | {sum(r['cost_usd'] or 0 for r in g) / len(g):.2f} | {sum(r['wall_seconds'] for r in g) / len(g):.0f} | "
            f"{sum(r['passed'] for r in g)}/{sum(r['checks'] for r in g)} | {sum(1 for r in g if r['critical_failures'])} | {sum(r['major_failures'] for r in g)} |"
        )
    lines += [
        "",
        "## By task and condition",
        "",
        "| Task | Cond. | Checks passed | Critical failures | Major failures | Failed checks |",
        "|---|---|---|---|---|---|",
    ]
    for t in ["T1", "T2", "T3", "T4", "T5", "T6"]:
        for cond in ["A", "B"]:
            g = [r for r in matrix if r["task"] == t and r["condition"] == cond]
            if not g:
                continue
            fails = " / ".join(
                f"r{r['rep']}: {r['failed_checks'] or 'none'}" for r in g
            )
            lines.append(
                f"| {t} | {cond} | {sum(r['passed'] for r in g)}/{sum(r['checks'] for r in g)} | {sum(r['critical_failures'] for r in g)} | {sum(r['major_failures'] for r in g)} | {fails} |"
            )
    pilots = [r for r in rows if r["run_id"].startswith("pilot")]
    if pilots:
        lines += [
            "",
            "## Pilot runs (excluded from the matrix by design, recorded for completeness)",
            "",
        ]
        for r in pilots:
            lines.append(
                f"- {r['run_id']}: cost ${r['cost_usd']:.2f}, {r['wall_seconds']:.0f} s, checks {r['passed']}/{r['checks']}, critical {r['critical_failures']}, major {r['major_failures']}"
            )
    lines += [
        "",
        "Two repetitions per cell are not evidence of broad statistical superiority; see docs/findings_memo.md for what the errors were.",
        "",
    ]
    (OUTPUT / "results.md").write_text("\n".join(lines))
    print(f"wrote {OUTPUT / 'results.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", action="store_true")
    main(ap.parse_args().table)
