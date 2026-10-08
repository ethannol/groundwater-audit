# Did dissolved nitrate decline at repeatedly sampled wells?

**Not supported.** Quantity: dissolved nitrate as N (USGS 00618, mg/L), routine groundwater samples from wells in San Bernardino County, early (2000–2011) versus late (2012–2023). The independent unit is the well.

**Pooled comparison (what it represents).** The median of all results was 1.99 mg/L (n=1337, 490 wells) in the early period and 1.60 mg/L (n=1098, 548 wells) in the late period. This compares two different, partly non-overlapping sets of wells, with unequal numbers of samples per well. Wells that were sampled many times are weighted more heavily. It describes the data collected, not change at any place. Only 190 wells are in both periods. 300 wells were sampled only early and 358 only late, so the apparent drop can come from which wells were sampled.

**Consistent cohort.** The 190 wells with a routine result in both periods, using each well's last result per period, have medians of 2.18 (early) and 1.86 (late). That gap is smaller in effect than it looks. Direction counts, using interval comparison so non-detects are determinate only when the intervals don't overlap:
- decline: 84
- increase: 101
- indeterminate: 5

A sign test on declines versus increases gives p≈0.24, so there is no evidence of a consistent direction. A well-level bootstrap of the median paired change (late minus early) gives a 95% CI of about −0.015 to +0.05 mg/L, which includes zero. The change is also centred near zero, so the lower cohort median does not reflect a systematic well-by-well decline.

**Caveats.**
- Non-detects (140 in the filtered rows, 8 and 7 in the cohort wells' last results) are treated as intervals [0, reporting limit], not substituted. Reporting limits varied from 0.02 to 0.6 mg/L, which could hide small changes at low concentrations.
- I excluded code 71851 (the same nitrate reported as NO3, which would double count), 00631 (nitrate+nitrite, a different quantity), total-fraction codes, field replicates, and non-groundwater media such as leachate and soil moisture.
- Last-result-per-period uses a single sample per well, which is noisy. Results are from one county and unweighted by well location or depth.

The pooled drop mainly reflects a change in which wells were sampled. At the repeatedly sampled wells, nitrate showed no clear decline.
