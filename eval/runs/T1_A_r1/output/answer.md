# Dissolved arsenic coverage, San Bernardino County wells (WQP/USGS NWIS snapshot)

The snapshot has 13,301 result rows. Of these, 11,748 are groundwater. The rest are leachate, elutriation, soil-moisture, interstitial and bulk-deposition samples, which I excluded. Within groundwater, 11,093 rows are routine and 582 are QC (578 field replicates, 4 reference materials). Another 73 have type "Not determined" and are neither routine nor QC.

Routine dissolved arsenic (USGS 01000) has 2,997 rows from 993 wells, collected between 2000-03-28 and 2023-05-05. Most wells have little history. The median well was sampled on one date, and only 490 wells have two or more distinct sample dates. The maximum is 19 dates at one well. Sampling was heaviest around 2009–2012 and 2016 (roughly 200–300 results a year). It fell to about 20–50 a year after 2019. So the record is mostly a one-time survey, and a trend analysis could only use a few hundred wells with uneven spacing.

There are 245 non-detect rows (8%): 242 "Not Detected" and 3 "Detected Not Quantified". Their values and units are blank, so they cannot be treated as numbers without substitution or a censored-data method. The associated limits run from 0.09 to 20 µg/L, which is a wide spread. Several different limit types are mixed together (laboratory reporting level, historical reporting limit, elevated detection limit and others). Limits that change over time can create false trends if non-detects are substituted. Note that 20 µg/L is above the 10 µg/L arsenic MCL.

Metadata gaps that matter for trends:
- Laboratory name is missing for 24% of rows, analysis date for 27%, and a few rows have no method ID.
- Project is blank for 98% of rows, and activity comment is blank for 58%.
- Sample depth is blank for about 92–95% of rows. SampleAquifer is always blank, although the station table has an aquifer name for 86% of wells.
- Station well depth is missing for 11% of wells and construction date for 20%.
- Activity end date, qualifier codes, and result-level coordinates are empty.

Changes in lab or method cannot be checked for a large share of the data. Well-depth and aquifer context is incomplete. All 993 wells do have a matching station record.
