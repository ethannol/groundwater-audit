import json
o=json.load(open("tmp_out.json")); x=o.pop("_extra")
o["share_declining"]=round(146/251,4)
o["nondetect_sensitivity"]=("Main method uses interval bounds (non-detect = [0, limit]); a pair is determinate only if intervals do not overlap. "
 "Substitution as sensitivity (labelled): zero -> 149 decline/108 increase/38 ties; half-limit -> 153/107/35; full-limit -> 152/108/35. "
 "Direction (more declines than increases) does not change; median late/early ratio 0.95-0.98. Only 31 cohort wells have a censored result in each period, so non-detects cannot drive the result. "
 "But limits vary 0.02-100 ug/L and rose in 2015-2018 (up to 100), and the early period has more censoring (11% vs 4% of results), which can mask or create apparent change for low-concentration wells.")
o["notes"]=("Filter: USGS 01000 dissolved As, ActivityTypeCode Sample-Routine, ActivityMediaSubdivisionName Groundwater (2997 of 3562 arsenic rows; excluded 162 field replicates, 34 undetermined, 1 reference material, 3 total-As 01002 rows, and elutriation/soil-moisture/interstitial/leachate rows). "
 "Units all ug/L, no conversion. 3 'Detected Not Quantified' rows treated as [0, reporting level]. Last result per well per period by date/time. "
 "Cohort 295 wells (659 early wells, 629 late wells; pooled comparison would mix different wells). 146 decline, 105 increase, 44 indeterminate. "
 f"Share declining of all cohort wells = {x['share_all']:.3f} (exact 95% CI {x['cp_all'][0]:.3f}-{x['cp_all'][1]:.3f}); among determinate wells 0.582 (CI 0.518-0.643). "
 f"Median ratio over {x['both']} both-detected wells, well bootstrap 95% CI {x['ratio_ci'][0]:.3f}-{x['ratio_ci'][1]:.3f}. "
 "Classification uses strict inequality of reported values with no analytic-error allowance, so small differences count as change. Methods changed over time (PLM10, PLM40/42, GF085, PLM62; some blank) and results are partly Preliminary.")
o["checks"]=["tabulated media, activity type, fraction, unit, detection condition, method, lab","all 01000 rows are Dissolved ug/L; no re-expressed duplicates","no duplicate well/date/time keys after filter; ResultIdentifier unique","censored limits tabulated by year; cohort vs pooled well counts compared"]
o["caveats"]=["wells not independent (spatial/aquifer clustering, shared labs and methods)","CI and sign-test p treat determinate wells as independent and exchangeable; p=0.011 is optimistic","selecting determinate wells conditions on outcome; all-well share is 0.49","cohort is wells sampled in both periods, not a random sample of the county","period endpoints are single samples, not period averages; last-sample timing varies within periods"]
json.dump(o,open("answer.json","w"),indent=1)
