import json
a={"recommendation":"cannot be determined",
"cohort_wells":30,"cohort_decline":0,"cohort_increase":0,"cohort_indeterminate":30,
"pooled_median_early":2.0,"pooled_median_late":0.91,
"data_problems_found":[
"Reporting limit changed 2 mg/L (2005) -> 0.2 mg/L (2018); 70% of 2005 results are non-detects '<2'",
"Cohort differs between periods: 30 wells (SYN-N*) sampled only in 2018, 30 wells (SYN-C*) in both",
"Lab B results (2018) have no result unit reported",
"Non-detect rows carry no result unit/value (only DL unit)",
"9 cohort wells have 2005 values identical to 2018 values (no change; possible duplication/synthetic artefact)"],
"rows_affected_by_each_problem":{
"Reporting limit change / 2005 non-detects":21,
"Wells only in 2018 (non-cohort)":30,
"Lab B results with unreported unit":8,
"Non-detect rows with blank result unit":21,
"Identical 2005/2018 values in 9 wells":18},
"notes":"Per-well directions use interval bounds (ND = [0,DL]). 21 of 30 cohort wells were '<2' in 2005, so any 2018 value <2 (21 of 30 wells) is indeterminate; the 9 wells with detected 2005 values show zero change (identical values). pooled_median_early=2.0 is the upper bound: the median is a non-detect, true value in [0,2]. Pooled late median 0.91 includes 30 wells absent in 2005 (cohort-only late median 1.435) and is not comparable. Lab B unit assumed mg/L as N only for sensitivity; excluding Lab B changes nothing (22/22 indeterminate).",
"checks":["unique (site,date) and ResultIdentifier: 0 duplicates","cohort_composition: 30/60 sites, 30 in both","censoring_profile: Lab A 2005 21/30 censored DL 2; 2018 0 censored DL 0.2","all rows: Nitrate, 00618, Dissolved, Groundwater, Sample-Routine; no QC/blank rows"],
"caveats":["Only 2 samples per cohort well; no independent replication or trend test possible","Synthetic data"]}
json.dump(a,open('answer.json','w'),indent=1)
open('answer.md','w').write("""# Basin Z nitrate: can we report a decline?

**Recommendation: cannot be determined. A decline is not supported.**

**Evidence.** The 30 wells sampled in both 2005 and 2018 give 0 declines, 0 increases and 30 indeterminate (non-detects treated as intervals [0, limit]; script `analysis.py`).
- 21 of the 30 wells were non-detect at a 2 mg/L reporting limit in 2005. Their 2018 values (0.6-1.5 mg/L) are all below 2, so they cannot be ranked against "<2".
- The other 9 wells have 2005 values (2.0-3.3 mg/L) identical to their 2018 values, so there is no change. The exact duplication is itself suspicious and should be checked with the source lab.

**Why the apparent drop is misleading.**
- The pooled medians (2005 <=2.0, a non-detect; 2018 0.91) mix different well sets. 30 wells (SYN-N*) were sampled only in 2018 and have low nitrate. The 2018 median for the 30 cohort wells alone is 1.44.
- The reporting limit fell tenfold, from 2 to 0.2 mg/L. 2018 low values are quantified, while the same concentrations in 2005 were censored.

**Other data issues.**
- The 8 results from Lab B in 2018 report no unit. Excluding them changes nothing.
- Non-detect rows have no result unit.
- Each well has one sample per period, so there is no within-well replication and no uncertainty estimate for a trend.

**What can be said.** Among the wells with a quantified 2005 result, nitrate did not change. For the rest, the 2005 data are too coarse to tell. To support a decline claim, re-censor 2018 at 2 mg/L, confirm Lab B's units, and use a consistent well set.
""")
