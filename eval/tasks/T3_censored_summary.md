# T3. Descriptive summary with censoring (arsenic)

Dataset: `data/wqp_result.csv` and `data/wqp_station.csv`.

Use routine groundwater results for dissolved arsenic (USGS parameter code
01000), in µg/L. Define two periods: early = 2000–2011 and late = 2012–2023
(by `ActivityStartDate` year). Treat each result as one observation (this
task is about censoring, not about wells).

Report in `answer.json`:

```json
{
  "early": {"n": <int>, "n_nondetect": <int>, "reporting_limit_min": <float>, "reporting_limit_max": <float>,
            "median_ugL": <float or null>, "share_above_10_ugL": <float or null>},
  "late":  {"n": <int>, "n_nondetect": <int>, "reporting_limit_min": <float>, "reporting_limit_max": <float>,
            "median_ugL": <float or null>, "share_above_10_ugL": <float or null>},
  "median_method": "<how non-detects were handled when computing the median>",
  "share_above_10_identifiable_in_both_periods": <true|false>,
  "notes": "<free text>"
}
```

In `answer.md`, state how non-detects were handled and why, whether the two
medians are comparable, and what the comparison does and does not show about
change in arsenic concentration.
