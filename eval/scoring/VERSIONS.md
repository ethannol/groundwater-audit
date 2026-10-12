# Scoring versions

The published evaluation is the original `eval/runs/*/score.json`,
`eval/scoring/scores.csv` and `eval/results.md` at source commit
`1f3c326964b7afcab64ab4f0cb1f6e564fee968c`. Those artifacts and the frozen tasks
are preserved. The portfolio presentation ledger derives historical claims
from those original files, not a revised score.

`eval/score.py` now writes **v2-schema-review** outputs under
`eval/scoring/v2/`, including a separate results table. It validates top-level
and nested answer shapes, rejects booleans/non-finite numbers where numbers
are requested, requires a named censored median method and a sensitivity
statement mentioning methods plus an outcome, and searches the explicit issue
inventory rather than unrelated notes. Adversarial tests exercise malformed
JSON shapes, meaningless long explanations and keyword mentions in notes.

These are mechanical gates, not proof of semantic correctness. Issue wording,
negation, weighting, scientific interpretation and volunteered analyses still
need the original human rubric. Re-scoring is an exploratory comparison and
must not silently replace the original reported pass rate.
