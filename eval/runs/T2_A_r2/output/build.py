import pandas as pd, json
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
g=d[(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaName=='Water')&(d.ActivityMediaSubdivisionName=='Groundwater')&(d.CharacteristicName=='Nitrate')]
a=g[(g.USGSPCode==618)&(g.ResultSampleFractionText=='Dissolved')].copy()
a['nondetect']=a.ResultDetectionConditionText.eq('Not Detected')
a['value_mg_L_as_N']=a.ResultMeasureValue
a['reporting_limit_mg_L_as_N']=a['DetectionQuantitationLimitMeasure/MeasureValue']
t=a[['OrganizationIdentifier','ActivityIdentifier','MonitoringLocationIdentifier','ActivityStartDate','USGSPCode','CharacteristicName','ResultSampleFractionText','value_mg_L_as_N','nondetect','reporting_limit_mg_L_as_N']]
assert not t.duplicated(['OrganizationIdentifier','ActivityIdentifier']).any()
t.to_csv('nitrate_as_n.csv',index=False)
print(len(t),t.MonitoringLocationIdentifier.nunique(),t.nondetect.sum(),t.reporting_limit_mg_L_as_N.describe())
print((g.USGSPCode==71851).sum(),g.USGSPCode.isin([620,71850]).sum())
