# Five-minute walkthrough

Script for talking a hiring manager through the project. Time marks are
approximate. Every number is in `reports/results.json` or `eval/results.md`.

## 0:00 The question (30 s)

Public groundwater chemistry data from the Water Quality Portal: USGS records
for wells in San Bernardino County, California, 2000–2023. Two constituents,
arsenic and nitrate. The analytical question is simple to state: did measured
concentrations decline at repeatedly sampled wells? The project question sits
on top of it: where does an LLM help produce a defensible answer, and where
does it introduce plausible errors that survive casual review?

## 0:30 The data are a minefield (60 s)

Open `data/processed/exclusion_log.csv`. Four things in this snapshot would
break a naive analysis:

1. 1,553 of 13,301 rows are leachate, soil moisture and elutriate samples
   collected at well sites. They are not groundwater.
2. Every nitrate sample appears twice, once as "mg/L as N" and once as "mg/L
   as NO3". Converting and pooling doubles the sample count.
3. Nitrate-plus-nitrite is a different chemical definition stored under its
   own name. It happens to equal nitrate in three quarters of samples here,
   but that is a finding, not an assumption.
4. Arsenic non-detect limits fell from about 2 µg/L to 0.1 µg/L as the
   laboratory changed. Substituting half the limit manufactures a decline.

## 1:30 The reference answer (90 s)

Show Figure 3 (`reports/figures/fig3_cohort_pairs.png`) and Figure 4.

- Pooled medians move: nitrate down, arsenic up. Neither is a change at
  wells; the late period sampled different wells. Figure 4 shows the pooled,
  one-per-well and cohort medians side by side.
- Nitrate, 190 cohort wells: 85 declines, 100 increases. No decline.
- Arsenic, 295 cohort wells: 145 declines, 106 increases, 44 indeterminate.
  The sign test says p = 0.016, but the median within-well ratio is 0.967, a
  3 percent change inside replicate precision, across a laboratory change.
  The honest statement is "slightly lower on average, comparable to
  measurement variability, no evidence of widespread decline."
- Non-detects are intervals, never substituted. Uncertainty uses the well as
  the independent unit. Everything is in `reports/report.md`, generated from
  the results file so the text cannot drift from the numbers.

## 3:00 The evaluation (90 s)

Six frozen tasks, one model (`claude-sonnet-5-5`), two conditions, two
repetitions: 24 bounded runs, each in an isolated directory with only the
data, the dictionary and the task. Condition A is a neutral prompt.
Condition B adds a structured workflow and generic validators, written
before the fixtures existed. Scoring is mechanical against the reference
answers for numbers, plus a written rubric for interpretation. See
`eval/results.md` for the table and `docs/findings_memo.md` for the
before/after examples.

Headline from the memo: 24 runs, 0 critical errors, 267 of 272 numerical
checks passed, $4.33 total. Both conditions handled every trap in the data.
The structured workflow added 30 percent cost and no accuracy. The residual
failures were a dropped code listed as included, two volunteered cohort
analyses on the same wells that pointed in opposite directions because of
unstated definitions, and one missed duplicated station row. All were caught
by reading against the reference definitions, not by the row counts.

## 4:30 What I would say in one sentence (30 s)

The resume bullet in `docs/resume_bullet.md`, which uses only measured
results. Human time saved was not measured; the protocol to measure it is in
`docs/human_time_protocol.md`.
