# Exploratory v2 re-score provenance

These outputs were generated on the Mac mini from scorer source commit
`8b26b4192c3d4a80e473e1b32273129a792dd9ba` using
`uv run python eval/score.py --table`. The original recorded answers and
reference JSON were reused; no model calls or new analytical fits were made.

The original published evaluation remains **267 of 272** checks passed.
The schema-hardened scorer gives **266 of 272**, with three major failures,
three minor failures and no critical failures. The additional composition
failure is a **scorer false negative**: T6_B_r1's explicit inventory correctly
describes the wells present in 2018 only, but the matcher recognized "only in"
and not "2018 only". The corrected v2.1 scorer adds that paraphrase and a
regression test; its outputs live separately under `eval/scoring/v2.1/`.
The original interpretive verdicts are joined for context, not newly adjudicated;
they continue to be marked for Ethan's review.

The original `eval/results.md`, `eval/scoring/scores.csv`, every original
per-run `score.json` and `reports/results.json` remain unchanged. Later
numeric-overflow hardening does not change the grades for these recorded answers.
