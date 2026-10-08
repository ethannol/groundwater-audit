import json
json.dump({
"cohort_wells":295,"decline":146,"increase":105,"indeterminate":44,
"share_declining":0.5817,"share_declining_denominator":"determinate wells",
"share_declining_ci95":[0.518,0.643],
"ci_method":"Clopper-Pearson exact binomial on 146 declines of 251 determinate wells; treats wells as independent, no spatial/temporal clustering adjustment, so likely somewhat too narrow",
"sign_test_p":0.0114,
"median_ratio_late_over_early_both_detected":0.9615,
"independent_unit":"The well (monitoring location): one last routine result per well per period gives one paired comparison per well. Wells are not truly independent (164 distinct 0.01-degree cells for 295 wells; shared aquifers, pumping and lab/method changes), so the independent-well assumption is approximate.",
"nondetect_sensitivity":"Direction does not change. Interval rule: 146 decline/105 increase/44 indeterminate. Zero substitution: 149/108/38; half-limit: 153/107/35; full-limit: 152/108/35. Declining share of determinate wells stays ~0.58-0.59; substitution makes indeterminate pairs look determinate and is not used for the headline.",
"notes":"Routine = ActivityTypeCode Sample-Routine, groundwater subdivision, USGS pcode 01000 (dissolved As, ug/L); field replicates, QC, soil-moisture/elutriation/leachate excluded. Non-detects and 'Detected Not Quantified' treated as intervals [0, reporting limit]. Both-detected pairs are determinate if values differ at all (no measurement-error allowance), so small differences count as change. 62 well-periods had several results on the last date; the last sorted by time was used. 31 wells have a non-detect in each period. Median ratio uses 257 both-detected wells. Reporting limits vary across years (0.1-100 ug/L)."
},open('answer.json','w'),indent=1)
