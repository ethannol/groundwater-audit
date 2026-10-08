# Basin Z nitrate: can we report a decline?

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
