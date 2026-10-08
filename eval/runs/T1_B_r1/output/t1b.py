import pandas as pd, json
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
g=d[d.ActivityMediaSubdivisionName=='Groundwater']
r=g[g.ActivityTypeCode=='Sample-Routine']
a=r[(r.CharacteristicName=='Arsenic')&(r.ResultSampleFractionText=='Dissolved')]
w=a.MonitoringLocationIdentifier.nunique(); print(w)
m=a.isna().mean(); m=m[(m>0.2)&(m<1)]; print(m)
allm=d.isna().mean(); mm=allm[(allm>0.2)&(allm<1)].index.tolist(); print(mm)
nd=a[a.ResultDetectionConditionText.notna()]
ans=dict(rows_total=len(d),rows_groundwater=len(g),rows_routine_groundwater=len(r),rows_qc_groundwater=582,
non_groundwater_media=d[d.ActivityMediaSubdivisionName!='Groundwater'].ActivityMediaSubdivisionName.value_counts().to_dict(),
arsenic_dissolved_routine_rows=len(a),arsenic_dissolved_routine_wells=w,arsenic_wells_with_2plus_samples=int((a.groupby('MonitoringLocationIdentifier').ActivityIdentifier.nunique()>=2).sum()),
arsenic_nondetect_rows=len(nd),arsenic_first_year=2000,arsenic_last_year=2023,arsenic_nondetect_limit_range_ugL=[0.09,20.0],
fields_with_material_missingness=mm,
notes="Groundwater defined by ActivityMediaSubdivisionName=Groundwater (all rows Water). QC = 578 field replicates + 4 reference materials; 73 'Not determined' groundwater rows are undetermined and excluded from routine. Dissolved arsenic is pCode 01000 only (the 3 Total/01002 rows excluded). Non-detect rows = 242 Not Detected + 3 Detected Not Quantified; none has a numeric result, all have limits in ug/l. Limits vary 0.09-20 ug/L and changed over time (about 0.2-2 before 2010, 0.09-0.13 later, one 20 in 2012), with mixed limit types. Wells counted by MonitoringLocationIdentifier; sample = ActivityIdentifier (no duplicates within well).",
checks=["ResultIdentifier unique (0 duplicates)","no duplicate (well, ActivityIdentifier) in routine dissolved arsenic","arsenic only in ug/l; no re-expression pairs","all methodspeciation blank","MeasureQualifierCode all blank"],
caveats=["Laboratory name missing for ~24% of arsenic rows, method for ~4%; station aquifer/well-depth metadata essentially absent (aquifer 100% missing, AquiferType 90%); lat/lon absent in result file; about 65% of wells have 2 or fewer dissolved-arsenic results (only 198 wells have 5 or more).","Censoring limits change over time, which can create or mask apparent trends; no substitution used."])
json.dump(ans,open('answer.json','w'),indent=1)
print(a.groupby('MonitoringLocationIdentifier').size().le(2).mean(), (a.groupby('MonitoringLocationIdentifier').size()>=5).sum())
