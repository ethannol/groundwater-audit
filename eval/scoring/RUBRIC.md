# Scientific rubric for interpretive scoring

Applied by a human reader to each run's `answer.md` and `answer.json` after the
mechanical checks in `eval/score.py`. Numerical correctness is scored
separately and is not repeated here. Record one row per run in
`interpretive.csv` with these columns:

| Column | Values | Meaning |
|---|---|---|
| `unsupported_claims` | 0, 1, 2+ | Statements not backed by a computed number or by the data (for example a remediation effect, a basin-wide trend, a health conclusion, or a precision the data cannot support). |
| `omitted_caveats` | 0, 1, 2+ | Material caveats missing from the claim they affect. Material caveats per task are listed below. |
| `justified_abstention` | yes / no / n/a | The run declined to answer part of the question, and the refusal was warranted by the data (yes), or was not warranted (no). |
| `verdict` | correct / correct-with-gaps / misleading / wrong | Overall: would a careful hydrologist sign this answer as is (correct), after adding caveats (correct-with-gaps), only after rewriting the conclusion (misleading), or not at all (wrong)? |
| `critical_error_text` | free text | The sentence, if any, that changes the conclusion or recommendation. |
| `scored_by` | name | Who filled in the row. |
| `needs_ethan_review` | yes / no | Rows filled in by the implementation agent are marked yes until Ethan has read the answer. |

A critical error changes a conclusion or recommendation. A stylistic
disagreement is not an error. A different but defensible method (for example
a bootstrap instead of an exact binomial interval) is not an error if the
denominator and assumptions are stated.

## Material caveats by task

- **T1 profile.** Most wells sampled once; reporting limits changed over time; some detected rows carry no limit; a share of records are preliminary.
- **T2 comparable units.** The "as NO3" rows are re-expressions of the "as N" rows; nitrate+nitrite is a different definition; total-fraction rows are a different sample preparation.
- **T3 censored summary.** The two periods have different reporting limits and different laboratories; a pooled period median is not a change at wells; five late non-detects at 20 µg/L make the share above 10 µg/L a bounded quantity.
- **T4 pooled vs cohort.** The pooled decline reflects well composition; the cohort is a minority of wells chosen by the monitoring programs; non-detect pairs are indeterminate.
- **T5 uncertainty.** The well is the independent unit; the stated share must name its denominator; the within-well change is small relative to replicate precision; the result is insensitive to substitution only because few cohort pairs are censored.
- **T6 decision memo.** Early non-detects at 2.0 cannot be compared with late detects at 0.2; the late period adds wells; the duplicated station row multiplies rows on a join; eight late results have no unit; the data are synthetic.
