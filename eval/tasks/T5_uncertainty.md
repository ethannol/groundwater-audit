# T5. Uncertainty assessment (arsenic)

Dataset: `data/wqp_result.csv` and `data/wqp_station.csv`.

Use routine groundwater results for dissolved arsenic (USGS parameter code
01000, µg/L). Periods: early = 2000–2011, late = 2012–2023. Consistent cohort:
wells with at least one routine result in both periods; use the last result
per well per period; classify each well's change as decline, increase or
indeterminate (a pair involving a non-detect is determinate only if the two
intervals do not overlap).

Report in `answer.json`:

```json
{
  "cohort_wells": <int>,
  "decline": <int>, "increase": <int>, "indeterminate": <int>,
  "share_declining": <float>,
  "share_declining_denominator": "<all cohort wells | determinate wells>",
  "share_declining_ci95": [<float>, <float>],
  "ci_method": "<text>",
  "sign_test_p": <float or null>,
  "median_ratio_late_over_early_both_detected": <float or null>,
  "independent_unit": "<text: what you treated as independent and why>",
  "nondetect_sensitivity": "<text: does the direction change under zero / half / full-limit substitution?>",
  "notes": "<free text>"
}
```

In `answer.md`, state what the data support about change at the cohort wells,
what precision is justified, and which assumptions the uncertainty statement
depends on.
