import pandas as pd, json
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
gw=d[(d.ActivityMediaName=='Water')&(d.ActivityMediaSubdivisionName=='Groundwater')]
print(gw.ActivityTypeCode.value_counts())
print('dup resid',d.ResultIdentifier.duplicated().sum())
rg=gw[gw.ActivityTypeCode=='Sample-Routine']
a=rg[(rg.CharacteristicName=='Arsenic')&(rg.ResultSampleFractionText=='Dissolved')].copy()
print(a.USGSPCode.value_counts(), a['ResultMeasure/MeasureUnitCode'].value_counts(dropna=False))
print(d[d.CharacteristicName=='Arsenic'].groupby(['ResultSampleFractionText','USGSPCode']).size())
print('dup act/well/date', a.duplicated(['MonitoringLocationIdentifier','ActivityIdentifier']).sum())
n=a.groupby('MonitoringLocationIdentifier').ActivityIdentifier.nunique()
print((n>=2).sum(), (a.groupby('MonitoringLocationIdentifier').size()>=2).sum())
nd=a[a.ResultDetectionConditionText.notna()]
print(nd.ResultDetectionConditionText.value_counts())
dl=nd['DetectionQuantitationLimitMeasure/MeasureValue']
print(dl.min(),dl.max(),dl.isna().sum(), nd['DetectionQuantitationLimitMeasure/MeasureUnitCode'].value_counts(dropna=False))
print(nd.ResultMeasureValue.notna().sum(), a.ResultMeasureValue.isna().sum(), (a.ResultMeasureValue.isna()&a.ResultDetectionConditionText.isna()).sum())
yr=pd.to_datetime(a.ActivityStartDate).dt.year
print(yr.min(),yr.max())
print(nd.groupby(pd.to_datetime(nd.ActivityStartDate).dt.year)['DetectionQuantitationLimitMeasure/MeasureValue'].agg(['count','min','max']))
print(a.LaboratoryName.isna().mean(), a['ResultAnalyticalMethod/MethodIdentifier'].isna().mean())
nonw=gw=None
d_gwmask=(d.ActivityMediaSubdivisionName=='Groundwater')
non=d[~d_gwmask].ActivityMediaSubdivisionName.value_counts().to_dict()
g=d[d_gwmask]
print(non, len(g), (g.ActivityTypeCode=='Sample-Routine').sum(), g.ActivityTypeCode.value_counts().to_dict())
st=pd.read_csv('data/wqp_station.csv',low_memory=False); print(st.isna().mean()[lambda s:s>0.2])
print(a.groupby('MonitoringLocationIdentifier').size().describe())
