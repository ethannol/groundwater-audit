# Did measured dissolved nitrate decline at repeatedly sampled wells?

**Not supported.** At the 190 wells with routine dissolved nitrate (00618, mg/L as N) in both 2000–2011 and 2012–2023, the last result fell at 84 wells, rose at 101, and was indeterminate at 5. A sign test on those directions gives p≈0.24, so there is no consistent decline. The cohort median moved from 2.18 to 1.86 mg/L. A well-level bootstrap interval for the change in cohort median is about −0.55 to +0.23 mg/L, which includes zero.

**Pooled versus cohort.** The pooled medians (early 1.99 mg/L from 1,337 results at 490 wells; late 1.60 mg/L from 1,098 results at 548 wells) summarize whichever wells and samples happened to be collected in each period. Only 190 wells appear in both periods; 300 appear only early and 358 only late. The pooled drop therefore mixes any real change with a change in which wells were sampled, and with wells that have many results counting more. Even so, its well-resampled interval (about −0.85 to +0.01 mg/L) barely excludes zero. The cohort comparison holds the wells fixed and uses one value per well and period, so well is the unit of analysis. It answers the question about repeatedly sampled wells, though these wells are not a random sample of the county.

**Data handling.**
- Only routine groundwater results for 00618 were used. Field replicates, "Not determined" activities, and leachate, soil-moisture and similar matrices were excluded.
- The nitrate+nitrite, total-fraction and as-NO3 parameters are different definitions or re-expressions, so they were excluded.
- The 140 non-detects were treated as intervals [0, reporting limit]. They are 3–11% of results per year, with limits of 0.02–0.06 mg/L (one 0.25 in 2016). Because the limits are far below typical concentrations (about 2 mg/L), they cannot change the medians. They made 5 cohort pairs indeterminate.
- Where a well had several results on its last day (8 cohort wells), taking the minimum or maximum instead changes the counts only to 86/99 or 85/100.

Caveat: using only the last result per period ignores seasonal and within-period variability.

Code: `analysis.py`, `ties.py`, `write_answer.py`.
