import pandas as pd, numpy as np, json
from validators import *
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
gw=d[(d.ActivityMediaName=='Water')&(d.ActivityMediaSubdivisionName=='Groundwater')]
rt=gw[gw.ActivityTypeCode=='Sample-Routine']
qc=gw[gw.ActivityTypeCode.str.contains('Quality Control')]
print(gw.ActivityTypeCode.value_counts())
print(d.groupby(['ActivityMediaSubdivisionName','ActivityTypeCode']).size())
a=rt[(rt.CharacteristicName=='Arsenic')&(rt.ResultSampleFractionText=='Dissolved')]
print(a.USGSPCode.value_counts(), a['ResultMeasure/MeasureUnitCode'].value_counts(dropna=False))
print(d[d.CharacteristicName=='Arsenic'].groupby(['ResultSampleFractionText','USGSPCode','ActivityMediaSubdivisionName']).size())
check_unique_key(a,['MonitoringLocationIdentifier','ActivityIdentifier','ResultIdentifier'])
check_unique_key(a,['MonitoringLocationIdentifier','ActivityIdentifier'])
nd=a[a.ResultDetectionConditionText.notna()]
print(nd.ResultDetectionConditionText.value_counts(), nd['DetectionQuantitationLimitMeasure/MeasureUnitCode'].value_counts(dropna=False))
print(nd['DetectionQuantitationLimitMeasure/MeasureValue'].describe(), nd.ResultMeasureValue.notna().sum())
print(a[a.ResultDetectionConditionText.isna()].ResultMeasureValue.isna().sum())
yr=a.ActivityStartDate.str[:4].astype(int)
per=a.groupby('MonitoringLocationIdentifier').ActivityIdentifier.nunique()
dates=a.groupby('MonitoringLocationIdentifier').ActivityStartDate.nunique()
print(per.describe(),(per>=2).sum(),(dates>=2).sum(), yr.min(),yr.max())
print(a.groupby('MonitoringLocationIdentifier').size().max())
censoring_profile(a.fillna({'ResultDetectionConditionText':''}).fillna(''),by=('LaboratoryName',)) if False else None
a2=a.copy(); a2['ResultDetectionConditionText']=a2.ResultDetectionConditionText.fillna(''); a2['DetectionQuantitationLimitMeasure/MeasureValue']=a2['DetectionQuantitationLimitMeasure/MeasureValue'].astype(str).replace('nan','')
censoring_profile(a2)
print(a.LaboratoryName.value_counts(dropna=False).head(), a.ResultStatusIdentifier.value_counts())
print(gw.groupby(gw.ActivityStartDate.str[:4]).size().tail(3))
print(rt.ActivityStartDate.min())
miss=d.isna().mean(); print(miss[(miss>0.05)&(miss<0.999)].round(2).to_string())
nongw=d[d.ActivityMediaSubdivisionName!='Groundwater'].ActivityMediaSubdivisionName.value_counts().to_dict()
dl=pd.to_numeric(nd['DetectionQuantitationLimitMeasure/MeasureValue'])
print(dl.min(),dl.max(),len(a),a.MonitoringLocationIdentifier.nunique())
ans=dict(rows_total=len(d),rows_groundwater=len(gw),rows_routine_groundwater=len(rt),rows_qc_groundwater=len(qc),
non_groundwater_media=nongw,arsenic_dissolved_routine_rows=len(a),arsenic_dissolved_routine_wells=int(a.MonitoringLocationIdentifier.nunique()),
arsenic_wells_with_2plus_samples=int((dates>=2).sum()),arsenic_nondetect_rows=len(nd),arsenic_first_year=int(yr.min()),arsenic_last_year=int(yr.max()),
arsenic_nondetect_limit_range_ugL=[float(dl.min()),float(dl.max())])
json.dump(ans,open('ans_partial.json','w'))
print(ans)
