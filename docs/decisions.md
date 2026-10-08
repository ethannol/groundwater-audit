# Decision log

Chronological record of scoping, data, and analytical decisions. Dates are the
date the decision was made. Numbers quoted here come from the probes or scripts
named in each entry.

## 2026-10-07 Scope confirmed with Ethan

- Model access: the Claude Code CLI on Ethan's own Claude account, run headless
  (`claude -p`). Costs are taken from the CLI's per-run `total_cost_usd` field.
- The USGS data snapshot may be committed (public domain).
- Multiple constituents are in scope. Sparse data is treated as part of the
  investigation (how LLM-driven analysis behaves when data are thin), not as a
  reason to drop a constituent.

## 2026-10-07 Region and constituents

Statewide Water Quality Portal site-summary scan (groundwater wells, results
since 2000, `dataProfile=periodOfRecord`). Counts are sites with results in at
least three distinct calendar years:

| County | Arsenic | Nitrate | Nitrate+nitrite as N |
|---|---|---|---|
| San Bernardino | 298 | 290 | 270 |
| Santa Barbara | 33 | 121 | 121 |
| Riverside | 88 | 86 | 78 |
| Kern | 31 | 31 | 31 |
| San Joaquin (first probe) | 19 | n/a | n/a |

Decision: San Bernardino County (FIPS 06071), both arsenic and nitrate.
Repeat sampling there comes largely from the USGS / Mojave Water Agency
cooperative monitoring program. The dense nitrate record and the sparser
arsenic record give one data-rich and one data-poor case under one pipeline.

Rejected: the GAMA bulk download page (returns HTTP 403 to non-browser
clients; the brief forbids browser automation on this machine). The WQX3
`fullPhysChem` profile (returned 99 rows plus an explicit
`ERROR: INCOMPLETE DATA` row for a query that returns 13,301 rows on the
legacy profile).

## 2026-10-07 Evaluation model and budget

- Model: whatever the CLI alias `sonnet` resolves to at run time, recorded per
  run from the CLI output (`modelUsage` canonical model id). First probe
  resolved to `claude-sonnet-5-5`.
- Budget bound per run: `--max-budget-usd` plus a wall-clock timeout, because
  this CLI version exposes no turn cap. Both values are recorded in the run
  config.

## 2026-10-07 Preparation rules (see data/processed/exclusion_log.csv)

- Groundwater medium only. The query asked for wells, but 1,553 rows are
  leachate, elutriate, soil-moisture, interstitial or bulk-deposition samples
  collected at well sites.
- Routine samples for analysis; field replicates kept separately (578 rows);
  "Not determined" (73) and reference-material (4) activity types excluded.
- USGS codes 71851/71850 ("mg/l asNO3") are NWIS re-expressions of 00618/00620
  ("mg/l as N"). Verified on 2,169 paired activities (ratio 4.36–4.47 against
  4.4266; deviations are 2-significant-figure rounding). Dropped, not
  converted, so nitrate samples are not double counted.
- Nitrate+nitrite (00631/00630) kept as its own family. It differs from
  nitrate alone by zero in 75% of paired samples and never occurs without
  00618, so it is not used for the trend question.
- Total-fraction rows (01002, 00620) kept in results_clean.csv only.
- Non-detects are intervals [0, limit] in canonical units. Three "Detected Not
  Quantified" rows are treated the same way and flagged.
- Preliminary and Historical status rows are kept and counted.

## 2026-10-07 Analytical choices

- Periods: early 2000–2011, late 2012–2023. Chosen to split the record at the
  point where arsenic reporting limits dropped to 0.1 µg/L and the USGS
  laboratory became the only analyst, so that the late period is internally
  more uniform.
- Target quantity: within-well change between the last routine sample of
  each period, over wells with samples in both periods. One pair per well
  makes the well the independent unit and avoids modelling within-well
  autocorrelation with the sparse data available.
- Censoring: Kaplan–Meier medians; direction of change by interval overlap;
  substitution only as a labelled sensitivity.
- Uncertainty: exact binomial interval and sign test on determinate pairs;
  well-level bootstrap (2,000 resamples, seed 20261007) over all pairs;
  Wilcoxon signed-rank on the both-detected subset as a secondary check.
- Kaplan–Meier quantile uses the lower-median convention (smallest value
  with F ≥ q). A floating-point tolerance of 1e-9 was added after a fixture
  test caught the product of survival terms landing just below 0.5.

## 2026-10-07 Evaluation freeze

- Pilot run `pilot_T1_A` (T1, Condition A, $0.15, 42 s) was used to check the
  harness. It exposed an ambiguity in T1 ("reporting limit range" did not say
  non-detect rows only); the task wording was tightened before the matrix
  started. The pilot is recorded and excluded from the matrix.
- Model: `claude-sonnet-5-5` (pinned id). Budget $3.00 per run, 1,800 s wall
  clock, tools Bash/Read/Write/Edit/Glob/Grep, no network tools.
- Isolation: each run works in a temporary directory under `~/.cache/gwaudit`
  containing only the snapshot, manifest, dictionary, task and (B) workflow;
  a separate virtualenv in the same cache directory provides Python.
  Known gap: the user's own `~/.claude/CLAUDE.md` is still loaded by the CLI;
  it contains pull-request guidance unrelated to analysis.
- The Condition B workflow and validators were written before the fixtures
  (commit order in git), and contain no dataset-specific numbers.

## 2026-10-07 Scoring adjustment made after the first T1 runs

T1 asks for "wells with 2+ samples". The reference counted distinct sampling
activities (521); run T1_A_r1 counted distinct sampling dates (490) and said
so. Both are defensible readings of the task text, so the scorer accepts
either. This adjustment applies identically to both conditions and is the
only scoring rule changed after runs were seen.
- Second refinement (after the T2 runs): run T2_B_r2 dropped the 71851 rows
  (row count correct, drop count correct, rationale in notes) but listed
  71851 under `pcodes_included`. The scorer had marked the code list as
  critical; it is now major, and the re-expression check also reads `notes`.
  The critical check for T2 is the row count, where double counting would
  show. Applied uniformly to all T2 runs.
- Third refinement (after the T3 runs): the three early "Detected Not
  Quantified" rows may be counted as non-detects (reference: 199) or not
  (196); both accepted. A median reported as null with explicit bounds in
  the method field is accepted as a bounded answer. Applied uniformly.
- Fourth refinement (after the T6 runs): the planted duplicate-station-row
  check matched the word "duplicate" in run T6_B_r2's remark about identical
  values, although that run never found the duplicated station row. The
  keyword list now requires a reference to the station row or the site id.
  Applied uniformly; it changes only that run's score.

## 2026-10-08 Evaluation matrix completed

All 24 runs recorded between 2026-10-07 23:37 and 2026-10-08 00:40 UTC
(sequential), no timeouts, no CLI errors, every run produced answer.json
and answer.md. Mechanical and interpretive scores are in
eval/scoring/scores.csv and eval/results.md. An unplanned fixture artefact:
the memo_bundle cohort wells have identical early and late values by
construction ("true concentrations identical"), and every T6 run flagged
the nine detected pairs as suspiciously identical. That is a correct
observation about the fixture, not an error, and a better fixture would add
measurement noise.
