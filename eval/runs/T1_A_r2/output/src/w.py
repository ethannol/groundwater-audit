import pandas as pd, json
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False).replace('',pd.NA)
m=d.isna().mean(); f=[c for c in d.columns if m[c]>0.05]
gw=d[d.ActivityMediaSubdivisionName=='Groundwater']
r=gw[gw.ActivityTypeCode=='Sample-Routine']
a=r[(r.CharacteristicName=='Arsenic')&(r.ResultSampleFractionText=='Dissolved')]
nd=a[a.ResultDetectionConditionText.notna()]
l=pd.to_numeric(nd['DetectionQuantitationLimitMeasure/MeasureValue'])
yr=pd.to_datetime(a.ActivityStartDate).dt.year
ng=d[d.ActivityMediaSubdivisionName!='Groundwater'].ActivityMediaSubdivisionName.value_counts()
out=dict(rows_total=len(d),rows_groundwater=len(gw),rows_routine_groundwater=len(r),
 rows_qc_groundwater=int(gw.ActivityTypeCode.str.startswith('Quality Control').sum()),
 non_groundwater_media={k:int(v) for k,v in ng.items()},
 arsenic_dissolved_routine_rows=len(a),arsenic_dissolved_routine_wells=int(a.MonitoringLocationIdentifier.nunique()),
 arsenic_wells_with_2plus_samples=int((a.groupby('MonitoringLocationIdentifier').ActivityIdentifier.nunique()>=2).sum()),
 arsenic_nondetect_rows=len(nd),arsenic_first_year=int(yr.min()),arsenic_last_year=int(yr.max()),
 arsenic_nondetect_limit_range_ugL=[float(l.min()),float(l.max())],
 fields_with_material_missingness=f,
 notes="QC = 578 field replicates + 4 reference materials; 73 groundwater rows have ActivityTypeCode 'Not determined' (neither routine nor QC; excluded from routine). Non-detect rows = 242 'Not Detected' + 3 'Detected Not Quantified' (the latter are below-quantitation, not zero); none carry a result value, limit is in DetectionQuantitationLimit fields (all ug/l). 2+ samples counted by distinct ActivityIdentifier; by distinct calendar date it is 490 wells. Placeholder values (HydrologicCondition 'Not determined', etc.) are non-empty so not counted as missing. Fields listed have >5% empty; many more are 100% empty (e.g. MeasureQualifierCode, ProjectName, MonitoringLocationName, SampleAquifer). Nitrate rows use mixed units (mg/l as N, mg/l asNO3) and are not part of the arsenic answers. Reporting limits vary 0.09-20 ug/L.")
json.dump(out,open('answer.json','w'),indent(2) if False else None) if False else json.dump(out,open('answer.json','w'),indent=2)
print(out)
