# Nitrate as N: comparable-unit table

**Scope.** Routine samples (`Sample-Routine`) with medium subdivision *Groundwater*. This drops 686 leachate, 180 elutriation, 242 soil-moisture, 55 interstitial and 3 bulk-deposition rows that carry the same activity type. It also drops field replicates, reference material and "Not determined" activities. The final table has 2,435 rows (one per site and activity) from 848 wells, with no duplicate keys.

**Same quantity.** `Nitrate` / Dissolved / 00618 (mg/L as N) and `Nitrate` / Dissolved / 71851 (mg/L as NO3) are the same measurement. 71851 appears in 2,301 activities, and every one of them also has a 00618 row. Where both have values (2,169 pairs), 00618/71851 = 0.2259 (CV 0.2%), which matches 14.0067/62.0049 = 0.22589. The 132 non-detects agree in both. I kept 00618 and dropped the 2,301 re-expressed 71851 rows, so nothing is counted twice. The 71851 values stay available through the conversion factor.

**Different quantities, excluded.**
- 00620 and 71850 are Total (unfiltered) nitrate, a different fraction (586 rows). They are not interchangeable with dissolved nitrate.
- 00630 and 00631 are nitrate **plus nitrite**, a different chemical definition. 00631 is dissolved but still includes nitrite, so I did not combine it with nitrate (`nitrate_plus_nitrite_combined = false`). 00630 is also a Total fraction.

**Non-detects.** 140 rows are "Not Detected", with no value and a reporting limit in mg/L as N. They are flagged `censored` and the limit is stored in `detection_limit_mgL_as_N`. I did not substitute any values. Downstream analysis needs interval bounds (0 to limit) or a censored estimator.

**What goes wrong if everything is pooled.**
1. Pooling 71851 without converting would inflate values by 4.43×. Pooling it after converting would double-count about 2,300 measurements, so those wells and dates would carry extra weight and the sample size would look about twice as large.
2. Adding the nitrate+nitrite and Total rows would mix definitions. Nitrate+nitrite is at least as large as nitrate, so results would be biased high. Total versus dissolved would add differences in sample treatment.
3. Pooling leachate, soil-moisture and similar media would mix non-groundwater samples into a groundwater estimate.
4. Non-detects have no numeric value and their reporting limits differ across rows, so naive pooling would drop them silently or mix limits.

**Caveats.** Result status (Preliminary, Historical, Accepted) was not filtered. Wells are repeatedly sampled, so rows are not independent and the well should be the unit in later analysis.
