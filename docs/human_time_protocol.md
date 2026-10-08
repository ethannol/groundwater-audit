# Optional protocol: measuring active analyst time

Status: **no human session has been run.** The evaluation in `eval/` records
model runtime, cost and errors. It says nothing about human time saved, and
nothing in this repository should be read as a measured speedup.

## What this protocol measures

Active analyst time to produce a checked answer to a matched analytical task,
with and without LLM assistance, including the time spent checking and
correcting the assistant's output. "Checked" means the analyst is willing to
sign the answer.

## Design

1. **Tasks.** Use the four unseen task templates in `docs/human_tasks/`
   (not the six frozen evaluation tasks, which the assistant's workflow was
   developed against). Each template has a matched pair: the same analytical
   operation on a different constituent or period, so the two members of a
   pair are of equal difficulty but not identical.
2. **Conditions.** Unassisted: the analyst works alone with Python and the
   data dictionary. Assisted: the analyst may use the Claude Code CLI with the
   Condition B prompt and workflow, but must check every number before
   signing.
3. **Order.** For each pair, flip a coin to decide which member is done
   unassisted; do the unassisted member first for pairs 1 and 3 and second for
   pairs 2 and 4 (ABBA order), so practice effects do not all land on one
   condition.
4. **Timing.** Start the clock when the task is opened, stop it when the answer
   is signed. Pause for interruptions. Record checking and correction time
   separately from drafting time (a second stopwatch, or note timestamps).
5. **Record.** One row per task in `docs/human_time_log.csv`:
   `date, pair, task, condition, order, drafting_minutes, checking_minutes,
   corrections_made, errors_found_in_assistant_output, signed (yes/no), notes`.
6. **Do not** backfill estimates for sessions that were not timed, and do not
   report model runtime or script runtime as human time.

## Reporting

Report the per-pair difference in total active minutes and the number of
corrections made. With four pairs, report the differences themselves and
their sign, not a p-value.
