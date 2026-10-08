import json
from scipy.stats import binomtest
p=binomtest(170,267).pvalue
i=json.load(open('t3_interim.json'))
e,l=i['early'],i['late']
ans={
"early":{k:e[k] for k in ["n","n_nondetect","reporting_limit_min","reporting_limit_max","median_ugL","share_above_10_ugL"]},
"late":{k:l[k] for k in ["n","n_nondetect","reporting_limit_min","reporting_limit_max","median_ugL","share_above_10_ugL"]},
"median_method":"Interval bounds: each non-detect bounded between 0 and its own reporting limit; median computed at both bounds. Early median bounds 1.9-2.0 (not unique, so reported as null with bounds in notes); late 3.3 at both bounds (identified). Half-limit substitution used only as a labelled sensitivity check (same values).",
"share_above_10_identifiable_in_both_periods":True,
"notes":f"Filter: USGSPCode 01000, dissolved, ug/L, ActivityType Sample-Routine, subdivision Groundwater (3559 -> 2997 rows; replicates, reference material, 'Not determined', and non-groundwater subdivisions dropped). 3 'Detected Not Quantified' rows (early, no value, limits 1.8-1.9) are excluded from medians/shares (counted in n). Early median bounds {e['median_bounds']}; late {l['median_bounds']}. Share>10 bounds early {e['share_above_10_bounds']}, late {l['share_above_10_bounds']} (late ND limits up to 20 ug/L make a few NDs ambiguous; early max limit 5 <10 so exactly identified). Shares are of 1802 early / 1192 late rows with value or ND. Limits changed from mostly 1-2 ug/L (early, up to 5) to ~0.1 ug/L (late), but ND share is only 11% vs 4%, and the medians lie above nearly all limits, so censoring barely affects them. Pooled wells differ (659 early vs 629 late; 295 in both). In the 295 shared wells (267 with differing per-well medians) the late per-well median is lower in 170, higher in 97, tied 28 (sign test p={p:.1e}); shared-well pooled share>10 rises 0.18->0.29 while per-well medians fall, so evidence is mixed. Repeated samples within wells are not independent; no CI given for pooled values.",
"checks":["no duplicate ResultIdentifier in arsenic rows","single characteristic/fraction/unit (ug/l); no re-expressed pairs","ND counts and limits by year tabulated (t3.py)","cohort comparison (t3b.py)"],
"caveats":["Pooled early vs late compares different well sets","Early 'Detected Not Quantified' rows excluded","Detected values sometimes below the listed limit (49 rows), listed limit may be a different limit type"]}
json.dump(ans,open('answer.json','w'),indent=1)
