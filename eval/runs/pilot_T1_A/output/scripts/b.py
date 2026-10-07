import pandas as pd
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
a=d[(d.ActivityMediaSubdivisionName=='Groundwater')&(d.ActivityTypeCode=='Sample-Routine')&(d.CharacteristicName=='Arsenic')&(d.ResultSampleFractionText=='Dissolved')]
print((a.groupby('MonitoringLocationIdentifier').ActivityIdentifier.nunique()>=2).sum())
t=a.groupby(['MonitoringLocationIdentifier','ActivityStartDate']).size();print(t[t>1].head(),(t>1).sum())
print(a.ActivityStartDate.str[:4].value_counts().sort_index().to_dict())
x=pd.to_numeric(a['DetectionQuantitationLimitMeasure/MeasureValue']);print(x.min(),x.max())
nd=a[a.ResultDetectionConditionText!='']
print(nd['DetectionQuantitationLimitMeasure/MeasureValue'].value_counts().head(8))
print(a.ActivityStartDate.str[:4].astype(int).groupby(a.MonitoringLocationIdentifier).agg(lambda s:s.max()-s.min()).describe())
