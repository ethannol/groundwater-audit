# Corrected schema re-score provenance

Generated on the Mac mini on 2026-10-12 from source commit
`686619672a10ccaa16526eafeeedd5a207c730d8` using
`uv run python eval/score.py --table`. It reused the original recorded answers
and reference JSON; there were no model calls or new analytical fits.

- Scorer SHA-256: `1df34d5540474afaf3574a86fc7ab4be4966bb447cbeb46421dc1907b7c43389`.
- Reference JSON SHA-256: `cc6d9012830aa82cf3135638d2b6ec8c6ef6b07a90f6f2c7fcc90ebfcc292c6b`.
- Matrix: 267 of 272 mechanical checks passed, two major failures, three minor
  failures and no critical failures. These checks mix numerical agreement with
  structured evidence and wording gates; they are not a semantic correctness rate.

The original published scores and the first schema scorer's outputs remain
unchanged. The [v2 provenance](../v2/PROVENANCE.md) records its false-negative
composition flag; this corrected edition recognizes "2018 only" in the
explicit issue inventory and tests that wording independently of notes.
Existing interpretive judgements are included for context, not re-adjudicated,
and continue to require Ethan's review.
