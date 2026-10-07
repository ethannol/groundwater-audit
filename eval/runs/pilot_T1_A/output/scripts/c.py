import pandas as pd,json
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
m=(d=='').mean()
f=[c for c in d.columns if m[c]>0.05]
j=dict(rows_total=13301,rows_groundwater=11748,rows_routine_groundwater=11093,rows_qc_groundwater=582,
non_groundwater_media={"Elutriation":385,"Interstitial":98,"Leachate":699,"Soil moisture":368,"Bulk deposition":3},
arsenic_dissolved_routine_rows=2997,arsenic_dissolved_routine_wells=993,arsenic_wells_with_2plus_samples=521,
arsenic_nondetect_rows=245,arsenic_first_year=2000,arsenic_last_year=2023,
arsenic_reporting_limit_range_ugL=[0.02,20.0],fields_with_material_missingness=f,
notes="QC = 578 field replicates + 4 reference materials; 73 groundwater rows have ActivityTypeCode 'Not determined' (neither routine nor QC, excluded from both). Wells with 2+ samples counted by distinct ActivityIdentifier (521); by distinct calendar date it is 490 (120 well-days have two activities). Non-detects are rows with ResultDetectionConditionText (242 Not Detected, 3 Detected Not Quantified); all have empty ResultMeasureValue. Reporting limits (0.02-20 ug/L) come from 2628 rows with a limit; 369 rows (incl. some non-detects possibly) have none; limit types are mixed (LRL, LT-MDL, blank-adjusted, DQCALC, etc.) and non-detect limits are mostly 1-2 ug/L, far above the 0.02-0.2 limits of later detects. Missingness list = result-file fields >5% empty; many are 100% empty.")
json.dump(j,open('answer.json','w'),indent=1)
