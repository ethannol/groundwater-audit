# Nitrate as N: comparable-unit table

**Table:** `nitrate_as_n.csv` has 2,435 rows, one per sampling activity, from 848 wells. 140 rows are non-detects. They have a blank result and a reporting limit, with no substitution. Scope is Sample-Routine activities in the Groundwater subdivision. QC replicates, reference material and "Not determined" activities are excluded. So are leachate, soil-moisture, elutriation and other non-groundwater water rows.

**Same quantity (included):** Nitrate, Dissolved, pcode 00618, mg/l as N. The (site, activity) key is unique.

**Same measurement re-expressed (dropped):** Pcode 71851 is dissolved nitrate reported as mg/L NO3. It exists for 2,301 of the 2,435 activities. Multiplying by 14.0067/62.0049 = 0.2259 reproduces 00618 within rounding (median difference 0.13%, max 1.4%). Non-detect status agrees in every pair. Keeping both would double-count 2,301 results. I dropped these 2,301 rows and kept the 00618 rows.

**Different quantities (excluded):**
- 00620 and 71850 are *total* (unfiltered) nitrate, as N and as NO3. They are a different fraction. These are the 586 rows counted as other-fraction.
- 00630 (total) and 00631 (dissolved) are nitrate **plus nitrite**. That is a different chemical definition, so nitrate and nitrite are not combined.

Dissolved and total nitrate are not shown to be equivalent here, so I did not merge them.

**What goes wrong if everything is pooled after unit conversion:**
- Each dissolved sample appears twice (00618 and 71851), which inflates n and gives some wells more weight.
- Total and dissolved fractions get mixed, along with nitrate and nitrate+nitrite. The nitrite part is usually small in oxic groundwater but is not zero.
- Pooled results would depend on which parameters each lab or period happened to report. Wells are not independent, so the inflated n also makes confidence intervals look too tight.
- Un-converted NO3 values are about 4.4 times larger than values as N. Mixing them would make nitrate look much higher against the 10 mg/L as N standard.
- Non-detect limits range from 0.02 to 0.25 mg/L as N and change by year and lab (for example 0.05–0.06 in the 2000s, 0.04 later). Substituting values would create apparent trends.

**Caveats:** Values flagged "Estimated" (about 190 rows in the groundwater routine subset before filtering) are retained. 134 activities have only 00618, so they have no 71851 partner. The units for the dropped 71851 rows and the "mg/l as N" label come from the NWIS metadata.
