# Nitrate comparable-unit preparation

**Scope.** Routine groundwater samples only (Sample-Routine, groundwater subdivision). That excludes field replicates, reference materials, leachate, soil moisture, and similar.

**Same quantity.** USGS parameter codes 00618 (dissolved nitrate, mg/L as N) and 71851 (dissolved nitrate, mg/L as NO3) describe the same measurement. NWIS computes the 00618 value from the NO3 value, or the reverse, in the same activity. All 2,301 71851 rows have a 00618 twin. After multiplying by 14.0067/62.0049 (0.2259) they agree to within rounding. They are one measurement written in two units, so I kept 00618 and dropped the 71851 rows (2,301). Summing or averaging both would double-count those samples. Using the NO3 rows without converting would inflate values by a factor of 4.43. The table has 2,435 rows from 848 wells, one row per activity. 140 are nondetects: the value is blank, flagged, and the detection limit is given.

**Not the same quantity.**
- 00620 (total nitrate, 472 rows) and 71850 (the NO3 form of total nitrate, 114 rows) measure the unfiltered fraction (586 rows excluded). They use a different method (ion chromatography) and a different sample fraction. Particulate or unfiltered nitrate is not equivalent to dissolved nitrate.
- 00631 (dissolved nitrate plus nitrite) and 00630 (total nitrate plus nitrite) are a different analyte. Nitrite is usually small in oxic groundwater, but the quantity differs, so I did not combine it with nitrate. This holds for about 2,300 dissolved records.

**What goes wrong if all nitrate rows are pooled after conversion.** Each activity would appear two to four times (00618, converted 71851, plus total-fraction and NO3 variants). The pooled data would give artificially small variances and wrong counts of samples and wells. Rows from the same well and date would be treated as independent. The mix of fractions and methods would add systematic offsets between records that look the same. Detection limits would also be mixed across different analytes. Trends and exceedance rates for the 10 mg/L as N standard would be biased, and nitrate+nitrite would blur the compound being regulated.

**Caveat.** The 00618 nondetect rows have a blank unit and fraction in the WQP export. I assigned them from the pcode and the detection-limit unit, which is mg/l as N.
