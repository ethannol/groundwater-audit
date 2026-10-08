# Findings memo: LLM-assisted groundwater analysis

For a hiring manager. Two pages. Every number comes from `eval/results.md`,
`eval/scoring/scores.csv`, `eval/scoring/interpretive.csv` or
`reports/results.json`. The interpretive judgements were made by the
implementation agent and are marked for Ethan's review in `interpretive.csv`.

## The question and the setup

Public USGS groundwater chemistry for San Bernardino County wells, 2000–2023,
arsenic and nitrate. The analytical question was whether measured
concentrations declined at repeatedly sampled wells. The project question was
where an LLM helps produce a defensible answer and where it introduces
plausible errors that survive casual review.

One model (`claude-sonnet-5-5`, via the Claude Code CLI), six frozen tasks,
two conditions, two repetitions: 24 runs, each in an isolated directory with
the data snapshot, its dictionary and the task, bounded to $3 and 30 minutes.
Condition A was a neutral prompt. Condition B added a structured workflow
(inspect metadata, establish comparability, treat non-detects as censored,
name the unit of analysis, compute in code, report uncertainty, abstain when
warranted) and generic validators. Answers were scored mechanically against a
checked reference analysis and then read against a written rubric.

## What happened

| | Condition A (neutral) | Condition B (workflow) |
|---|---|---|
| Runs | 12 | 12 |
| Numerical checks passed | 135 of 136 | 132 of 136 |
| Runs with a critical error | 0 | 0 |
| Major failures | 0 | 2 |
| Interpretive verdict: correct / correct-with-gaps | 11 / 1 | 7 / 5 |
| Total cost | $1.88 | $2.45 |
| Total wall time | 11.5 min | 15.6 min |
| Agent turns | 76 | 109 |

Per run: $0.13–0.28 and 31–200 seconds. No run timed out, errored, or hit the
budget. A separate pilot run was used to check the harness and is recorded
separately.

**What worked.** Every run, in both conditions:

- excluded the 1,553 leachate, soil-moisture and elutriate samples that the
  portal returns for "well" sites;
- recognised that nitrate "as NO3" rows are the same measurement as the "as
  N" rows and dropped them rather than converting and double counting (the
  trap in task T2; the row count of 2,435 was reproduced by all four runs);
- kept nitrate-plus-nitrite and total-fraction rows out of the comparable
  table, with reasons;
- treated non-detects as intervals or bounded the median, never substituted
  as the main method;
- said that the pooled period comparison (nitrate median 1.99 to 1.60 mg/L)
  reflects which wells were sampled and that the 190-well cohort shows no
  decline (task T4, four of four runs "not supported");
- named the well as the independent unit, gave a denominator for the share
  of declining arsenic wells, and said spatial clustering makes the interval
  too narrow (task T5);
- refused to support a decline on the synthetic Basin Z data (task T6) and
  found the limit change, the composition change and the missing units.

**What failed.** Nothing changed a conclusion. The failures were:

1. *Inconsistent reporting.* Run T2_B_r2 dropped the re-expressed nitrate
   rows correctly, reported the right row count and the right drop count,
   then listed the dropped code under "included". A reviewer reading only the
   JSON would be misled; a reviewer reading the memo would not.
2. *Volunteered analyses with silent definitions.* Task T3 asked for pooled
   period summaries. Both Condition B runs added an unrequested cohort
   analysis. One reported that per-well medians fell at 170 of 295 shared
   wells (p ≈ 1e-5); the other reported that the pooled median within the
   same shared wells rose from 2.2 to 2.7 µg/L. Both numbers reproduce from
   the data. They point in opposite directions because one weights each well
   once and the other weights by sampling frequency, and neither run said
   so in a way a reader could compare. This is the clearest example of a
   plausible result that survives casual review.
3. *One missed planted issue.* Run T6_B_r2 did not find the duplicated
   station row. Its validators checked result-table keys but not the station
   table it was about to join.
4. *Small factual slips.* "Aquifer name is entirely absent" (T1_B_r1; the
   field is present for 86% of stations, a different field is empty); "only
   one late non-detect is unresolved" (T3_B_r2; there are five).

**What caught the failures.** The reference row counts caught nothing,
because the counts were right. The failures were caught by reading the
answers against the reference *definitions* and by re-running the
volunteered calculations. Mechanical scoring would have passed items 2 and 4
and, before a correction, passed item 3. Four of the scorer's own rules had
to be corrected after seeing runs (two ambiguous task wordings, one
mis-calibrated severity, one false-positive keyword); all four corrections
are logged in `docs/decisions.md` and applied to both conditions. The
reference harness made more mistakes than the model did.

## What the structured workflow did and did not do

It did not reduce errors on these tasks with this model. It added cost
(+30%), time (+36%) and turns (+43%), and the extra turns went partly into
validator output and partly into extra analyses the task had not asked for,
which is where two of the interpretive gaps came from. Condition A already
did the things the workflow prescribes, which is a statement about this
model's defaults on a well-specified task, not about workflows in general.

A caveat that limits all of this: tasks T4 and T5 spelled out the cohort
rule, the period boundaries and the interval rule for non-detects. They
measure execution fidelity given a stated method more than method choice.
Tasks T1, T3 and T6 were less prescriptive, and T6, the least prescriptive,
was still answered correctly by all four runs.

## Which tasks appear worth assisting

On this evidence, all six: data profiling, comparable-unit preparation,
censored summaries, cohort comparison, uncertainty statements and a
decision memo were each produced correctly for well under a dollar and
under four minutes, from a cold start, with the method traps in the data
handled. The condition on that statement is a precise task specification and
a reviewer who checks definitions, not just numbers. The place to spend
review effort is on anything the model adds beyond the question asked.

## What is not claimed

- No human time saved. No human session was timed; the protocol is in
  `docs/human_time_protocol.md`.
- No ranking of models or prompts beyond these 24 runs. Two repetitions per
  cell show consistency, not superiority.
- No statement about arsenic or nitrate beyond the reference report's: no
  nitrate decline at the cohort wells; a small, statistically detectable but
  practically minor arsenic shift that coincides with laboratory and
  reporting-limit changes.

## Open items for Ethan

- Read the 24 answers and confirm or change the interpretive verdicts
  (`eval/scoring/interpretive.csv`, column `needs_ethan_review`).
- Decide whether the T3 volunteered-analysis gap counts as an unsupported
  claim or as helpful initiative; the memo treats it as the former.
- If a second model or a less prescriptive task set is wanted, the runner
  and scorer take them without change.
