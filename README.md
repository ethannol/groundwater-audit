# Groundwater Audit

*Where does an LLM help produce a defensible groundwater analysis, and where
can it introduce plausible errors that survive casual review?*

A bounded case study. It pairs a checked reference analysis of public
groundwater chemistry data with a small, reproducible evaluation of
LLM-assisted analysis under two conditions. Everything here runs locally from
a fresh checkout without new model calls, except the evaluation runner, which
is a separate command.

## The analytical question

Did measured concentrations of dissolved **arsenic** and dissolved **nitrate**
decline at repeatedly sampled wells in San Bernardino County, California,
between 2000–2011 and 2012–2023?

Two constituents were kept on purpose: nitrate has a dense repeat-sampling
record and arsenic a sparse one, so the same pipeline is exercised on a
data-rich and a data-poor case.

## Main findings

**Reference analysis** (`reports/report.md`, numbers from `reports/results.json`):

- The pooled nitrate median fell (1.99 to 1.60 mg/L as N) and the pooled
  arsenic median rose (1.9 to 3.3 µg/L) between periods. Neither is a change
  at wells. Only a minority of wells were sampled in both periods, and the
  late period sampled different wells.
- At the 190 nitrate wells sampled in both periods, 85 declined and 100
  increased (5 indeterminate because of non-detects). The data do not
  support a nitrate decline at repeatedly sampled wells.
- At the 295 arsenic cohort wells, 145 declined and 106 increased (44
  indeterminate; sign test p = 0.016). The median within-well ratio among
  detected pairs is 0.967, a change of about 3 percent, which is inside the
  replicate precision of the measurements and coincides with a change of
  laboratory and a ten-fold drop in reporting limit. Measured arsenic was
  slightly lower on average at the cohort wells, by an amount comparable to
  measurement variability, with no evidence of a widespread decline.
- The dataset carries four traps that a casual analysis would fall into:
  1,553 non-groundwater samples at well sites; nitrate reported twice per
  sample in two units; nitrate-plus-nitrite as a separate chemical
  definition; and arsenic non-detect limits that fell from about 2 to 0.1
  µg/L across the record.

**Evaluation** (`eval/results.md`, `docs/findings_memo.md`): 24 runs of
`claude-sonnet-5-5` on six frozen tasks, two conditions, two repetitions,
$4.33 in total. Zero critical errors; 267 of 272 numerical checks passed.
Every run handled the four data traps above. The structured-workflow
condition cost 30 percent more and did not reduce errors. The failures that
did occur were definitional: a dropped code listed as included, volunteered
cohort analyses on the same wells pointing opposite ways because of unstated
weighting, and one missed duplicated station row. Reading answers against the
reference definitions caught them; the row counts did not. The scoring
harness itself needed four logged corrections.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). Tested on macOS.

```bash
uv venv --python 3.12
uv pip install -e ".[dev]"
```

## Commands

Deterministic, no model calls:

```bash
.venv/bin/python -m gwaudit.acquire --verify      # checksums of the committed snapshot
.venv/bin/python -m gwaudit.prepare               # data/processed/*  (comparability + QC, with exclusion log)
.venv/bin/python -m gwaudit.analysis              # reports/results.json, reports/tables/, reports/figures/
.venv/bin/python -m gwaudit.report                # reports/report.md from results.json
.venv/bin/python -m pytest                        # 33 tests: units, censoring, joins, grouping, uncertainty, fixtures
.venv/bin/python eval/fixtures/make_fixtures.py   # regenerate the synthetic fixtures (deterministic)
.venv/bin/python eval/scoring/build_reference.py  # reference answers for the frozen tasks
.venv/bin/python eval/score.py --table            # separate exploratory v2 re-score; preserves original published scores
gwaudit-presentation                            # derive presentation claims from original results and scores
```

Re-download the snapshot (network; the portal returned byte-identical files
on two downloads on 2026-10-07):

```bash
.venv/bin/python -m gwaudit.acquire
```

Make new model calls (costs money; uses the Claude Code CLI on the logged-in
account; bounded to $3.00 and 30 minutes per run):

```bash
.venv/bin/python eval/run_eval.py --plan          # show the 24-run matrix and what is recorded
.venv/bin/python eval/run_eval.py --task T4 --condition B --rep 1
.venv/bin/python eval/run_eval.py --all           # runs every cell not yet recorded
```

## Data provenance

Read the [linked weighting failure example](docs/definition-failure.md) to see
how two extra analyses of the same cohort suggested opposite directions.
[Scoring versions](eval/scoring/VERSIONS.md) distinguishes the published
evaluation from schema-hardened exploratory re-scoring. The portfolio's
secondary numbers come from `reports/presentation.json`, derived from the
unchanged reference results and original scores.

- Source: Water Quality Portal legacy web services, result profile
  `resultPhysChem`, San Bernardino County (FIPS 06071) wells, characteristics
  Arsenic, Nitrate, and Inorganic nitrogen (nitrate and nitrite), results
  from 2000-01-01. Query: `data/raw/query.json`. Download date, URLs, portal
  count headers and SHA-256 checksums: `data/raw/manifest.json`.
- All 13,301 result rows are USGS NWIS records (public domain), so the
  snapshot is committed unchanged in `data/raw/`.
- Field definitions: `data/dictionary/wqp_fields.csv`, extracted from the
  portal user guide saved alongside it.
- The WQX3 profile was tried and returned an explicit incomplete-data error
  for this query; the GAMA bulk download refuses non-browser clients. Both
  are recorded in `docs/decisions.md`.

## Layout

```
data/raw/            snapshot, query, manifest (never modified)
data/dictionary/     field definitions
data/processed/      prepared tables and the exclusion log (regenerated by gwaudit.prepare)
src/gwaudit/         acquire, units, censoring, prepare, analysis, report
tests/               focused tests incl. fixture invariance checks
reports/             report.md, results.json, figures/, tables/
eval/tasks/          six frozen tasks           eval/prompts/   the two condition prompts
eval/workflow/       Condition B workflow + validators (written before the fixtures)
eval/fixtures/       synthetic fixtures with truth.json (SYNTHETIC=1 on every row)
eval/run_eval.py     bounded runner             eval/score.py   mechanical scoring
eval/scoring/        reference.json, RUBRIC.md, interpretive.csv, scores.csv
eval/runs/<run_id>/  config, prompt, CLI result (cost, usage), stdout, output/ (answer.json, answer.md, scripts)
eval/results.md      results table (both conditions, costs, runtimes, errors)
docs/                decisions.md, findings_memo.md, walkthrough.md, resume_bullet.md, human_time_protocol.md
```

## What this project does not claim

- No remediation effect, aquifer-wide improvement, or health conclusion is
  inferred from the before/after comparison.
- No human time saved. The reference analysis is a correctness reference,
  not a productivity baseline. `docs/human_time_protocol.md` describes how
  to measure analyst time; no such session has been run.
- Two repetitions per task and condition are not evidence of broad
  statistical superiority of either condition.
