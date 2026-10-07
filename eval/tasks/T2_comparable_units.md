# T2. Comparable-unit preparation (nitrate)

Dataset: `data/wqp_result.csv` and `data/wqp_station.csv`.

Build one table of *dissolved nitrate results expressed as mg/L as N*, one row
per sampling activity, from routine groundwater samples only (medium
groundwater, `ActivityTypeCode` = `Sample-Routine`). Decide, and justify, which
`CharacteristicName`, `USGSPCode`, `ResultSampleFractionText` and unit
combinations belong in that table. Save the table as `nitrate_as_n.csv`.

Report in `answer.json`:

```json
{
  "rows_in_table": <int>,
  "wells_in_table": <int>,
  "nondetect_rows_in_table": <int>,
  "pcodes_included": [<USGSPCode>, ...],
  "pcodes_excluded": {<USGSPCode>: "<reason>", ...},
  "unit_conversion_factors_used": {"<from unit> -> mg/L as N": <factor>, ...},
  "rows_dropped_as_same_measurement_reexpressed": <int>,
  "rows_excluded_other_fraction": <int>,
  "nitrate_plus_nitrite_combined": <true|false>,
  "notes": "<free text>"
}
```

In `answer.md`, explain which rows measure the same quantity and which do
not, and what would go wrong if all nitrate rows were pooled after unit
conversion.
