The snapshot has 13,301 result rows for San Bernardino County wells (2000 onward). Of these, 11,748 are groundwater, and 11,093 of those are routine samples. The other 1,553 rows are leachate, elutriation, soil moisture, interstitial or bulk-deposition water. Groundwater QC rows number 582 (578 field replicates, 4 reference materials). A further 73 groundwater rows are typed "Not determined", so they are neither routine nor QC.

Routine dissolved arsenic (01000, µg/L) has 2,997 results from 993 wells, one result per sample, from 28 Mar 2000 to 5 May 2023. Coverage is thin per well. 472 wells have a single sample and only 521 have two or more (490 if counted by distinct calendar date). The median well has one sampling date, the mean is 2.7, and the maximum is 19. Sampling effort is uneven through time. It peaks at about 230–300 results a year in 2009–2011 and 2016, and falls to 21–54 a year in 2019–2022. Any trend analysis will therefore rest on a small set of repeatedly sampled wells, and the network composition changes over time.

245 results (8%) are non-detects: 242 "Not Detected" and 3 "Detected Not Quantified". None has a result value. The limit is in the DetectionQuantitationLimit fields, in µg/L, and ranges from 0.09 to 20. Most limits are 1 µg/L (129 rows), with others at 0.2, 0.26, 1.9, 2 and a few at 20. Changing limits over time can create artificial trends unless the non-detects are handled with censored-data methods. The 3 "Detected Not Quantified" rows are below quantitation and should not be treated as zero.

Metadata gaps:
- Many fields are entirely empty, including MeasureQualifierCode, ProjectName, MonitoringLocationName, SampleAquifer and the data-quality fields.
- Sample depth is about 90% missing, and the depth reference point is missing at a similar rate.
- ProjectIdentifier is 98% missing.
- LaboratoryName is 58% missing and AnalysisStartDate 64% missing.
- Analytical method is missing for about 14% of rows.
- Result status is mixed: 1,721 Accepted, 1,190 Preliminary and 86 Historical.
- Several fields carry the placeholder "Not determined" (e.g. HydrologicCondition), so they look populated but hold no information.

Because depth, method and laboratory are often unknown, changes in method or screened interval cannot be separated from real change over time.
