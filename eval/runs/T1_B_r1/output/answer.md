# T1 data profile: dissolved arsenic, San Bernardino County wells

The snapshot has 13,301 result rows, all medium "Water". Of these, 11,748 are groundwater. The other 1,553 are leachate (699), elutriation (385), soil moisture (368), interstitial (98) and bulk deposition (3), and I excluded them. Among groundwater rows, 11,093 are routine, 582 are quality control (578 field replicates and 4 reference materials), and 73 are "Not determined". The undetermined rows are neither routine nor QC, so I left them out of the routine set.

Routine dissolved arsenic (`CharacteristicName` Arsenic, fraction Dissolved, USGS parameter code 01000) has 2,997 rows from 993 wells. The 3 Total-fraction rows (code 01002) are a different quantity and are excluded. All arsenic is reported in ug/L, so no unit conversion was needed. There are no duplicate result IDs or duplicate well/activity pairs. Results run from 2000 to 2023, which is the start of the query window and the latest sample.

Sampling is sparse per well. 521 wells have two or more samples. About 65% of wells have two or fewer results, and only 198 have five or more. The independent unit is the well, and repeated samples from one well are not independent. Any trend analysis needs a well-level approach, and the set of wells almost certainly changes between periods.

There are 245 non-detect rows (8.2%): 242 "Not Detected" and 3 "Detected Not Quantified". None has a numeric value. Their reporting limits range from 0.09 to 20 ug/L. Limits were mostly 0.2–2 ug/L before 2010 and about 0.1 ug/L in later years, with a single 20 ug/L in 2012. Limit types are mixed. Because limits changed over time, an apparent decline in arsenic could be an artefact. Non-detects need interval bounds or a censored estimator, not substitution.

Metadata gaps:
- Laboratory name is missing for about 24% of arsenic rows, and analysis date for about 27%.
- Sample depth fields are 92–96% empty.
- Aquifer name is entirely absent, and aquifer type is about 90% missing in the station file.
- These gaps limit stratification by aquifer or depth and any lab-effect checks.
- About 12% of all result rows have no numeric value, mostly non-detects.
- Many result rows have no quality-control or comment context.

Evidence, checks and caveats are in `answer.json`. The scripts are `t1.py` and `t1b.py`.
