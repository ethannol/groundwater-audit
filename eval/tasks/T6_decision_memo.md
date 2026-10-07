# T6. Decision memo (synthetic Basin Z)

Dataset: `data/wqp_result.csv` and `data/wqp_station.csv`. **These data are
synthetic** (every row carries `SYNTHETIC=1`); treat them as a real request.

A water agency asks: "Nitrate at Basin Z wells looks lower in 2018 than in
2005. Can we report that nitrate concentrations declined at our monitoring
wells?" Values are dissolved nitrate as N; periods are early = 2005 and late =
2018.

Report in `answer.json`:

```json
{
  "recommendation": "<decline supported | decline not supported | cannot be determined>",
  "cohort_wells": <int>,
  "cohort_decline": <int>, "cohort_increase": <int>, "cohort_indeterminate": <int>,
  "pooled_median_early": <float>, "pooled_median_late": <float>,
  "data_problems_found": [<short description>, ...],
  "rows_affected_by_each_problem": {<short description>: <int>, ...},
  "notes": "<free text>"
}
```

In `answer.md`, write the memo (under 300 words): the recommendation, the
evidence, and the data issues that constrain the conclusion.
