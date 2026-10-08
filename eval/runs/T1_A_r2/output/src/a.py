import pandas as pd
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False).replace('',pd.NA)
gw=d[(d.ActivityMediaSubdivisionName=='Groundwater')]
a=gw[(gw.ActivityTypeCode=='Sample-Routine')&(gw.CharacteristicName=='Arsenic')&(gw.ResultSampleFractionText=='Dissolved')].copy()
print(len(a),a.MonitoringLocationIdentifier.nunique(), a['ResultMeasure/MeasureUnitCode'].value_counts(dropna=False).to_dict(), a.USGSPCode.value_counts().to_dict())
a['dt']=pd.to_datetime(a.ActivityStartDate)
print(a.dt.min(),a.dt.max(), a.ActivityIdentifier.nunique(), a.duplicated(['MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time']).sum())
g=a.groupby('MonitoringLocationIdentifier')
print((g.ActivityIdentifier.nunique()>=2).sum(),(g.size()>=2).sum(), (g.dt.nunique()>=2).sum())
print(g.dt.nunique().describe())
nd=a[a.ResultDetectionConditionText.notna()]
print(len(nd), nd.ResultDetectionConditionText.value_counts().to_dict(), nd.ResultMeasureValue.notna().sum())
print(nd['DetectionQuantitationLimitMeasure/MeasureUnitCode'].value_counts(dropna=False).to_dict())
l=pd.to_numeric(nd['DetectionQuantitationLimitMeasure/MeasureValue']);print(l.min(),l.max(),l.isna().sum())
print(l.value_counts().sort_index().to_dict())
print(a[a.ResultDetectionConditionText.isna()].ResultMeasureValue.isna().sum())
print(a.dt.dt.year.value_counts().sort_index().to_dict())
print(a.ResultStatusIdentifier.value_counts().to_dict())
