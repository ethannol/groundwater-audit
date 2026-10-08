# Arsenic change at San Bernardino County cohort wells (early 2000–2011 vs late 2012–2023)

**Quantity.** Dissolved arsenic (USGS 01000, µg/L), routine groundwater samples, last result per well per period, for the 295 wells sampled in both periods. Non-detects are treated as intervals [0, limit], not substituted.

**What the data support.** Of 295 wells, 146 declined, 105 increased and 44 are indeterminate. Among the 251 determinate wells, 58% declined (exact 95% CI 52–64%). Among all 295 wells the share is 49% (CI 44–55%). The median late/early ratio at the 257 wells with detections in both periods is 0.96 (well-bootstrap CI 0.93–1.00). A modest tilt toward lower concentrations is plausible, but the change is small. It is not a clear county-wide decline, and many wells rose. A sign test on determinate wells gives p = 0.011.

**Precision.** Report roughly "55–60% of determinate wells declined", not a figure to the second decimal. The p-value and the CIs are probably too optimistic. They assume wells are independent, but nearby wells share aquifers, laboratories and methods. They also assume each endpoint sample represents its period.

**Non-detects.** Substituting zero, half-limit or full limit leaves the direction unchanged (149–153 declines vs 107–108 increases). Only 31 cohort wells have a non-detect in either period. Reporting limits varied from 0.02 to 100 µg/L, and the early period was more heavily censored (11% vs 4% of results). Changing limits can hide or create change at low-concentration wells.

**Assumptions the uncertainty depends on.**
- Wells are independent units. This is likely violated by spatial clustering.
- Any difference in reported values counts as change, with no allowance for analytic error. Methods changed over time, and some results are Preliminary. Part of the 146 + 105 split is probably noise.
- Restricting to determinate wells conditions on the outcome. The all-well share is 49%, so the "58% declining" figure depends on that choice.
- The cohort is wells that happened to be sampled twice. It is not a random sample of the county, so the result does not generalise beyond these wells.
- Single last samples can reflect seasonal or pumping variation rather than a trend.
