# T4. Pooled versus consistent-cohort comparison (nitrate)

Dataset: `data/wqp_result.csv` and `data/wqp_station.csv`.

Use routine groundwater results for dissolved nitrate as N (USGS parameter
code 00618, mg/L as N). Periods: early = 2000–2011, late = 2012–2023.

1. Pooled comparison: the median of all results in each period.
2. Consistent cohort: wells with at least one routine result in both periods.
   For each cohort well use the last result in each period, and classify the
   change as decline, increase, or indeterminate (a pair involving a non-detect
   is determinate only if the two intervals do not overlap).

Report in `answer.json`:

```json
{
  "pooled_early": {"n": <int>, "wells": <int>, "median": <float>},
  "pooled_late":  {"n": <int>, "wells": <int>, "median": <float>},
  "cohort_wells": <int>,
  "wells_only_early": <int>, "wells_only_late": <int>,
  "cohort_early_median": <float>, "cohort_late_median": <float>,
  "cohort_decline": <int>, "cohort_increase": <int>, "cohort_indeterminate": <int>,
  "did_nitrate_decline": "<yes|no|not supported>",
  "notes": "<free text>"
}
```

In `answer.md`, answer the question "Did measured dissolved nitrate decline at
repeatedly sampled wells between the two periods?" and explain what the
pooled comparison represents versus the cohort comparison.
