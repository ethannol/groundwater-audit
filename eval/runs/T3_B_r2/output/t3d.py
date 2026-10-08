import json
o=json.load(open('/tmp/out.json'))
def blk(p):
    x=o[p]; return dict(n=x['n'],n_nondetect=x['n_nondetect'],reporting_limit_min=x['rl_min'],reporting_limit_max=x['rl_max'],
      median_ugL=round((x['med_lo']+x['med_hi'])/2,3),share_above_10_ugL=round((x['share_lo']+x['share_hi'])/2,4))
a=dict(early=blk('early'),late=blk('late'),
 median_method="No substitution as main method. Medians computed as interval bounds (non-detects = 0 vs = their reporting limit); early bounds 1.9-2.0, late 3.3-3.3, midpoint reported. Non-detect limits lie below the median for ~89% (early) and ~89% (late) of censored rows, and the median is essentially identified (bounds differ <=0.1 ug/L).",
 share_above_10_identifiable_in_both_periods=True,
 notes="Population: USGS pcode 01000 dissolved arsenic, Sample-Routine, ActivityMediaSubdivisionName=Groundwater (2997 rows; 562 of 3559 pcode-01000 rows dropped: field replicates, reference material, 'Not determined' activity, and elutriation/soil-moisture/interstitial/leachate subdivisions). Units all ug/L, no conversion; ResultIdentifier unique; no re-expressed pairs. n_nondetect counts 'Not Detected' only (early 196, late 46); 3 early 'Detected Not Quantified' rows (no value, limit ~1.8) are also treated as left-censored in the median bounds. Reporting-limit min/max are over censored rows. Share >10: bounds early 0.156-0.156, late 0.308-0.312 (a non-detect with limit 20 in 2012 is the only unresolved one). Limits changed over time (early median-limit ~1-2 ug/L, 0.02-0.2 lower limits from 2006 on; late mostly 0.1) and censoring fell from ~11% to ~4%, but with limits below the medians this affects the medians little. Pooled periods have different wells (659 early vs 629 late, only 295 in both); on the 295 shared wells the medians are 2.2 vs 2.7 and share>10 is 0.179 vs 0.286, so the pooled increase is smaller in median but same direction. Multiple samples per well are not independent; no well-level uncertainty was computed here, so differences are descriptive.",
 checks=["tabulate_fields on pcode 01000 rows","check_unique_key ResultIdentifier: 0 duplicates","check_reexpressed_pairs: none","censoring_profile by period/year: limits vary 0.02-20 ug/L","cohort_composition via set intersection: 295 common wells"],
 caveats=["Pooled comparison confounded by changing well sets and labs/methods","No well-level uncertainty","369 detected rows lack a reported limit; 49 detected values are below their limit (estimated)"])
json.dump(a,open('answer.json','w'),indent=1)
print(a['early'],a['late'])
