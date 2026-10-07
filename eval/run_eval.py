"""Evaluation runner: bounded headless Claude Code runs on frozen tasks.

    python eval/run_eval.py --plan                 # print the run matrix, no model calls
    python eval/run_eval.py --task T1 --condition A --rep 1
    python eval/run_eval.py --all                  # all runs not yet recorded
    python eval/run_eval.py --pilot                # one smoke-test run, labelled pilot

Each run gets a fresh, isolated working directory outside this repository that
contains only the data snapshot, the manifest, the field dictionary, the task,
and (Condition B) the workflow and validators. The model has no access to the
reference analysis, the scoring code, fixture truth files, or other runs.

Artifacts for each run are saved under eval/runs/<run_id>/:
    config.json      model, budget, timeout, command line, timestamps
    prompt.txt       the exact prompt sent
    result.json      the CLI's JSON result (cost, usage, duration, turns)
    stdout.txt / stderr.txt
    output/          answer.json, answer.md and every other file the model wrote
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "eval"
RUNS = EVAL / "runs"
MODEL = "claude-sonnet-5-5"          # exact id; the alias 'sonnet' resolved to this on 2026-10-07
MAX_BUDGET_USD = 3.00                # per run
TIMEOUT_S = 1800                     # per run wall clock
TOOLS = "Bash,Read,Write,Edit,Glob,Grep"
REPS = (1, 2)
CONDITIONS = ("A", "B")
TASKS = {
    "T1": ("T1_profile.md", "real"),
    "T2": ("T2_comparable_units.md", "real"),
    "T3": ("T3_censored_summary.md", "real"),
    "T4": ("T4_pooled_vs_cohort.md", "real"),
    "T5": ("T5_uncertainty.md", "real"),
    "T6": ("T6_decision_memo.md", "fixture:memo_bundle"),
}
PINNED = ["pandas==3.0.6", "numpy==2.5.3", "scipy==1.18.1", "matplotlib==3.11.2"]
CACHE = Path.home() / ".cache" / "gwaudit"


def ensure_env() -> Path:
    """A separate virtualenv for the model, outside the repository."""
    env = CACHE / "venv"
    py = env / "bin" / "python"
    if not py.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        subprocess.run(["uv", "venv", "--python", "3.12", str(env)], check=True)
        subprocess.run(["uv", "pip", "install", "--python", str(py), *PINNED], check=True)
    return py


def stage_workdir(task: str, condition: str, workdir: Path) -> None:
    (workdir / "data").mkdir(parents=True)
    _, source = TASKS[task]
    if source == "real":
        for f in ["wqp_result.csv", "wqp_station.csv", "manifest.json"]:
            shutil.copy(ROOT / "data" / "raw" / f, workdir / "data" / f)
    else:
        fx = EVAL / "fixtures" / source.split(":")[1]
        for f in ["wqp_result.csv", "wqp_station.csv"]:
            shutil.copy(fx / f, workdir / "data" / f)
        (workdir / "data" / "manifest.json").write_text(json.dumps({
            "source": "SYNTHETIC fixture generated for evaluation; not real observations",
            "fields": "same layout as a Water Quality Portal resultPhysChem export"}, indent=2))
    shutil.copy(ROOT / "data" / "dictionary" / "wqp_fields.csv", workdir / "data" / "wqp_fields.csv")
    shutil.copy(EVAL / "tasks" / TASKS[task][0], workdir / "TASK.md")
    if condition == "B":
        shutil.copy(EVAL / "workflow" / "ANALYST_WORKFLOW.md", workdir / "WORKFLOW.md")
        shutil.copy(EVAL / "workflow" / "validators.py", workdir / "validators.py")
    # make the inputs read-only so the snapshot cannot be altered in place
    for p in (workdir / "data").iterdir():
        p.chmod(0o444)


def run_one(task: str, condition: str, rep: int, label: str | None = None) -> dict:
    run_id = label or f"{task}_{condition}_r{rep}"
    out = RUNS / run_id
    if (out / "result.json").exists():
        print(f"{run_id}: already recorded, skipping")
        return json.loads((out / "config.json").read_text())
    py = ensure_env()
    prompt = (EVAL / "prompts" / f"condition_{condition.lower()}.md").read_text().replace("{python}", str(py))
    tmp = Path(tempfile.mkdtemp(prefix=f"gwaudit_{run_id}_", dir=str(CACHE)))
    workdir = tmp / "work"
    stage_workdir(task, condition, workdir)
    cmd = ["claude", "-p", prompt, "--model", MODEL, "--output-format", "json",
           "--no-session-persistence", "--tools", TOOLS, "--max-budget-usd", f"{MAX_BUDGET_USD:.2f}",
           "--dangerously-skip-permissions"]
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE")}
    env["HOME"] = os.environ["HOME"]
    started = dt.datetime.now(dt.UTC)
    try:
        proc = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True, timeout=TIMEOUT_S, env=env)
        timed_out = False
        stdout, stderr, rc = proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        timed_out = True
        stdout = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        rc = None
    ended = dt.datetime.now(dt.UTC)
    out.mkdir(parents=True, exist_ok=True)
    (out / "prompt.txt").write_text(prompt)
    (out / "stdout.txt").write_text(stdout)
    (out / "stderr.txt").write_text(stderr)
    result = None
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError:
        pass
    if result is not None:
        (out / "result.json").write_text(json.dumps(result, indent=2))
    # collect everything the model wrote (not the staged inputs)
    outdir = out / "output"
    outdir.mkdir(exist_ok=True)
    staged = {"TASK.md", "WORKFLOW.md", "validators.py", "data"}
    for p in workdir.iterdir():
        if p.name in staged:
            continue
        if p.is_dir():
            shutil.copytree(p, outdir / p.name, dirs_exist_ok=True)
        else:
            shutil.copy(p, outdir / p.name)
    config = {
        "run_id": run_id, "task": task, "condition": condition, "rep": rep, "label": label,
        "task_file": TASKS[task][0], "data_source": TASKS[task][1],
        "model_requested": MODEL, "max_budget_usd": MAX_BUDGET_USD, "timeout_s": TIMEOUT_S, "tools": TOOLS,
        "command": cmd[:1] + ["-p", "<prompt.txt>"] + cmd[3:],
        "started_utc": started.isoformat(timespec="seconds"), "ended_utc": ended.isoformat(timespec="seconds"),
        "wall_seconds": round((ended - started).total_seconds(), 1), "timed_out": timed_out, "return_code": rc,
        "cost_usd": result.get("total_cost_usd") if result else None,
        "model_used": list((result or {}).get("modelUsage", {}).keys()),
        "num_turns": result.get("num_turns") if result else None,
        "duration_api_ms": result.get("duration_api_ms") if result else None,
        "is_error": result.get("is_error") if result else True,
        "answer_json_present": (outdir / "answer.json").exists(),
        "answer_md_present": (outdir / "answer.md").exists(),
    }
    (out / "config.json").write_text(json.dumps(config, indent=2))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"{run_id}: cost ${config['cost_usd']}, {config['wall_seconds']}s, turns {config['num_turns']}, "
          f"answer.json={config['answer_json_present']}, error={config['is_error']}")
    return config


def plan():
    rows = [(t, c, r) for t in TASKS for c in CONDITIONS for r in REPS]
    print(f"{len(rows)} runs; model {MODEL}; budget ${MAX_BUDGET_USD}/run; timeout {TIMEOUT_S}s; tools {TOOLS}")
    for t, c, r in rows:
        done = (RUNS / f"{t}_{c}_r{r}" / "result.json").exists()
        print(f"  {t} {c} rep{r}  {'recorded' if done else 'pending'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--pilot", action="store_true", help="one labelled smoke-test run on T1/A, excluded from the matrix")
    ap.add_argument("--task"); ap.add_argument("--condition"); ap.add_argument("--rep", type=int)
    a = ap.parse_args()
    if a.plan:
        plan(); sys.exit(0)
    if a.pilot:
        run_one("T1", "A", 0, label="pilot_T1_A"); sys.exit(0)
    if a.all:
        for t in TASKS:
            for c in CONDITIONS:
                for r in REPS:
                    run_one(t, c, r)
        sys.exit(0)
    run_one(a.task, a.condition, a.rep)
