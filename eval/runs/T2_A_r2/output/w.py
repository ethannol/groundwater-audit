import json
json.dump({"rows_in_table":2435,"wells_in_table":848,"nondetect_rows_in_table":140,
"pcodes_included":["00618"],
"pcodes_excluded":{"71851":"Same dissolved nitrate measurement as 00618, re-expressed as mg/L NO3; dropped as duplicate (2301 rows, each paired with a 00618 row in the same activity)",
"00620":"Total (unfiltered) nitrate as N: different fraction",
"71850":"Total nitrate as NO3: re-expression of 00620 and other fraction",
"00631":"Dissolved nitrate+nitrite as N: different analyte (CharacteristicName 'Inorganic nitrogen (nitrate and nitrite)')",
"00630":"Total nitrate+nitrite as N: different analyte and fraction"},
"unit_conversion_factors_used":{"mg/l as N -> mg/L as N":1.0,"mg/l asNO3 -> mg/L as N":0.2259},
"rows_dropped_as_same_measurement_reexpressed":2301,
"rows_excluded_other_fraction":586,
"nitrate_plus_nitrite_combined":False,
"notes":"Filter: ActivityTypeCode=Sample-Routine, medium Water/Groundwater (excludes elutriation, leachate, soil moisture, interstitial, bulk deposition subdivisions; QC replicates excluded). Kept CharacteristicName=Nitrate, Dissolved, pcode 00618 (mg/l as N), one row per activity (no duplicates). No row required conversion since 71851 (mg/L NO3 = 14.007/62.004 = 0.2259 x N) always duplicates a 00618 row; in 2169 paired detected rows the ratio is 4.43 as expected. 140 non-detects have no value (blank) with reporting limit in mg/l as N (0.02-0.25 where given); left as censored, not substituted. Some 00618 values are NWIS-computed from 71851/other, others measured by IC; both are same quantity. Estimated-value flags (208 rows overall) not removed."},open('answer.json','w'),indent=1)
open('answer.md','w').write("""# Nitrate comparability

**Same quantity (kept):** dissolved nitrate, pcode 00618, reported as mg/L as N. Each such result has a partner row, pcode 71851, which is the *same* measurement expressed as mg/L NO3. 71851 is about 4.43 times 00618 (NO3/N mass ratio 62.004/14.007), as the 2169 detected pairs confirm. Converting 71851 with a factor of 0.2259 simply reproduces 00618, so the 2301 NO3 rows were dropped as re-expressions, not extra data. The table has 2435 rows, one per activity, from 848 wells. 140 are non-detects with a blank value and a reporting limit. I left them censored and did not substitute a value.

**Different quantities (excluded):**
- Total (unfiltered) nitrate, 00620 (as N) and 71850 (as NO3): a different sample fraction. These are 586 rows, and 71850 re-expresses 00620.
- Nitrate+nitrite ("Inorganic nitrogen (nitrate and nitrite)", 00631 dissolved and 00630 total): a different analyte, so they were not combined with nitrate. Nitrite adds to the total and is usually small in oxic groundwater, but it is not nitrate.
- Non-groundwater media (leachate, elutriation, soil moisture, interstitial, deposition) and QC samples (replicates and reference material): not routine groundwater samples.

**What would go wrong if all nitrate rows were pooled after unit conversion:** after converting to N, every dissolved result would be counted twice (00618 and 71851). That would inflate sample size and make the dates look independent, and it would weight wells with both rows more heavily. Converting 71851 as if it were already N would also give values 4.4 times too high. Mixing total with dissolved fractions, or adding nitrate+nitrite, would shift the distribution and the exceedance rates against the 10 mg/L as N standard. Leachate and soil-moisture samples would add non-aquifer water. Pseudo-replication would also understate the uncertainty of any trend or test.
""")
