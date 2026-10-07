# T1. Data profile

Dataset: `data/wqp_result.csv` (results) and `data/wqp_station.csv` (sites).

Definitions for this task:
- A *routine groundwater result* is a row whose medium is groundwater
  (`ActivityMediaName` = `Water` and `ActivityMediaSubdivisionName` =
  `Groundwater`) and whose `ActivityTypeCode` is `Sample-Routine`.
- *Dissolved arsenic* means `CharacteristicName` = `Arsenic` with
  `ResultSampleFractionText` = `Dissolved` (USGS parameter code 01000).

Report in `answer.json`:

```json
{
  "rows_total": <int, all rows in wqp_result.csv>,
  "rows_groundwater": <int, rows whose medium is groundwater>,
  "rows_routine_groundwater": <int>,
  "rows_qc_groundwater": <int, groundwater rows whose ActivityTypeCode is a quality-control type>,
  "non_groundwater_media": {<ActivityMediaSubdivisionName>: <row count>, ...},
  "arsenic_dissolved_routine_rows": <int>,
  "arsenic_dissolved_routine_wells": <int, distinct MonitoringLocationIdentifier>,
  "arsenic_wells_with_2plus_samples": <int>,
  "arsenic_nondetect_rows": <int, routine dissolved arsenic rows with a non-empty ResultDetectionConditionText>,
  "arsenic_first_year": <int>, "arsenic_last_year": <int>,
  "arsenic_nondetect_limit_range_ugL": [<min>, <max>, of the detection/reporting limits on the non-detect rows only],
  "fields_with_material_missingness": [<field name>, ...],
  "notes": "<free text>"
}
```

In `answer.md`, describe the coverage in a paragraph: wells, samples, dates,
sampling frequency, non-detects and reporting limits, and any metadata gaps
that would limit a trend analysis.
