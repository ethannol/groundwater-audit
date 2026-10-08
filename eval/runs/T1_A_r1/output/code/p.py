import pandas as pd
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
print(len(d))
print(d.groupby(['ActivityMediaName','ActivityMediaSubdivisionName']).size())
print(d.ActivityTypeCode.value_counts())
g=d[(d.ActivityMediaName=='Water')&(d.ActivityMediaSubdivisionName=='Groundwater')]
print(g.ActivityTypeCode.value_counts())
print(g.groupby(['CharacteristicName','ResultSampleFractionText','USGSPCode']).size())
r=g[g.ActivityTypeCode=='Sample-Routine']
a=r[(r.CharacteristicName=='Arsenic')&(r.ResultSampleFractionText=='Dissolved')]
print(len(a),a.MonitoringLocationIdentifier.nunique())
print(a.USGSPCode.value_counts(), a['ResultMeasure/MeasureUnitCode'].value_counts())
# samples per well: distinct activity/date
a=a.assign(dt=a.ActivityStartDate)
c=a.groupby('MonitoringLocationIdentifier').dt.nunique()
print((c>=2).sum(), (a.groupby('MonitoringLocationIdentifier').size()>=2).sum(), c.describe())
print(a.dt.min(),a.dt.max(), a.ActivityStartDate.str.len().value_counts())
print(a.duplicated(['MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time']).sum())
nd=a[a.ResultDetectionConditionText!='']
print(len(nd), nd.ResultDetectionConditionText.value_counts())
print(nd[['ResultMeasureValue','DetectionQuantitationLimitMeasure/MeasureValue','DetectionQuantitationLimitMeasure/MeasureUnitCode','DetectionQuantitationLimitTypeName','ResultMeasure/MeasureUnitCode','MeasureQualifierCode']].drop_duplicates().to_string())
print(a[a.ResultMeasureValue==''].shape, a.MeasureQualifierCode.value_counts())
print(a.ActivityStartDate.str[:4].value_counts().sort_index().to_dict())
m=(d=='').mean().sort_values(ascending=False); print(m.to_string())
