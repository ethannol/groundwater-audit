import json
p={
"unit_missing_censored_2005":"2005 non-detects (21 rows) have blank result unit; limit 2 mg/L as N",
"unit_missing_labB_2018":"Lab B 2018 results (8 rows, wells C00-C07) have no result unit",
"reporting_limit_change":"Reporting limit fell from 2 (2005) to 0.2 mg/L as N (2018)",
"cohort_mismatch":"60 wells in 2018 but only 30 in 2005; 30 N-wells have 2018 only",
"identical_values":"9 cohort wells have identical 2005 and 2018 values (suspected copied/carried values)",
"duplicate_station_row":"Duplicate station row for SYN-C03 in wqp_station.csv"}
a={"recommendation":"cannot be determined","cohort_wells":30,"cohort_decline":0,"cohort_increase":0,"cohort_indeterminate":30,
"pooled_median_early":2.0,"pooled_median_late":0.91,
"data_problems_found":list(p.values()),
"rows_affected_by_each_problem":{p["unit_missing_censored_2005"]:21,p["unit_missing_labB_2018"]:8,p["reporting_limit_change"]:90,p["cohort_mismatch"]:30,p["identical_values"]:18,p["duplicate_station_row"]:1},
"notes":"Early pooled median is not identifiable: 21/30 results are <2 mg/L as N, so the median is <=2.0 (2.0 is an upper bound, not an estimate). Late pooled median 0.91 uses all 60 wells incl. 30 late-only wells; cohort-only late median 1.435. Cohort: 21 wells ND(<2) then 0.6-1.8 detected (direction unidentifiable, interval overlap); 9 wells unchanged (detected, identical values). No well shows a determinable decline or increase. Substitution was not used as main method.",
"checks":["unique ResultIdentifier and (ActivityIdentifier,USGSPCode): 0 duplicates","single characteristic/fraction/pcode/method: Nitrate, Dissolved, 00618, SYN01; all Sample-Routine groundwater (no QC rows)","cohort_composition: 30 wells in both periods, 30 only in 2018","censoring: 2005 21/30 censored at 2; 2018 0/60 censored at 0.2","no re-expressed pairs (single parameter code)"],
"caveats":["Lab B unit missing; if reported as NO3 the late median would be ~0.72 rather than 0.91","2 mg/L limit hides whether early values were below the 2018 results","one result per well per period; no uncertainty beyond per-well direction counts"]}
json.dump(a,open('answer.json','w'),indent=1)
open('answer.md','w').write("""# Basin Z nitrate memo (synthetic data)

**Recommendation: cannot be determined.** Do not report that nitrate declined.

**Evidence.** Only the 30 wells sampled in both 2005 and 2018 can show a change. Of these, 21 had non-detects in 2005 (<2 mg/L as N) and 0.6-1.8 mg/L detected in 2018. A result of "<2" is compatible with a rise, a fall or no change, so these wells' direction is indeterminate. The other 9 wells have detected values identical to the last digit in both years. Per-well tally: 0 declines, 0 increases, 30 indeterminate.

The apparent drop comes from the pooled comparison. The 2005 pooled median is only bounded: at most 2.0 mg/L as N, because 21 of 30 results are censored. The 2018 pooled median is 0.91, but that uses 60 wells, including 30 wells never sampled in 2005. The 2018 median for the 30 matched wells is 1.435.

**Data issues constraining the conclusion.**
- The reporting limit fell from 2 to 0.2 mg/L as N. The high 2005 limit hides the early values and cannot be compared with 2018 detections (21 rows in 2005; the limit differs for all 90 rows).
- The 21 non-detects have no result unit recorded (limit unit is mg/l as N).
- The 8 Lab B results from 2018 (wells C00-C07) have no unit. If they were nitrate as NO3 rather than N, the pooled late median would be about 0.72.
- Well sets differ between years (30 wells 2018-only).
- 9 wells show identical values in both years, which suggests carried-forward or copied data (18 rows).
- Station table has a duplicate row for SYN-C03.

Each well has one result per period.
""")
