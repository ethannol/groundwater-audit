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
