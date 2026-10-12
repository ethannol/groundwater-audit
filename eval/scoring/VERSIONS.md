# Scoring versions

The published evaluation is the original `eval/runs/*/score.json`,
`eval/scoring/scores.csv` and `eval/results.md` at source commit
`1f3c326964b7afcab64ab4f0cb1f6e564fee968c`. Those artifacts and the frozen tasks
are preserved. The portfolio presentation ledger derives historical claims
from those original files, not a revised score.

The recorded **v2-schema-review** outputs under `eval/scoring/v2/` include a
separate results table. The corrected **v2.1-schema-review** scorer now writes
to `eval/scoring/v2.1/`, preserving both earlier versions. It validates top-level
and nested answer shapes, rejects booleans/non-finite numbers where numbers
are requested, requires a named censored median method and a sensitivity
statement mentioning methods plus an outcome, and searches the explicit issue
inventory rather than unrelated notes. Adversarial tests exercise malformed
JSON shapes, meaningless long explanations and keyword mentions in notes.

These are mechanical gates, not proof of semantic correctness. Issue wording,
negation, weighting, scientific interpretation and volunteered analyses still
need the original human rubric. Re-scoring is an exploratory comparison and
must not silently replace the original reported pass rate.

Artifact review caught a false negative in v2's narrower composition keyword
match: T6_B_r1 says "2018 only", correctly identifying a changed well set in
the explicit issue inventory. v2.1 accepts that wording and tests it without
notes, while retaining the test that unrelated notes cannot count as issue
identification. This correction is applied to every recorded answer and needs
no new model calls. The v2 provenance document records its erroneous extra flag.
