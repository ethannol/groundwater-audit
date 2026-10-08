import pandas as pd, numpy as np, json
F=14.0067/62.0049
d=pd.read_csv('data/wqp_result.csv',dtype=str)
n=d[(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')&(d.CharacteristicName=='Nitrate')]
oth=n[(n.ResultSampleFractionText!='Dissolved')&n.USGSPCode.isin(['00618','71851','00620','71850'])]
n=n[n.USGSPCode.isin(['00618','71851'])].copy()
n['v']=pd.to_numeric(n.ResultMeasureValue);n['dl']=pd.to_numeric(n['DetectionQuantitationLimitMeasure/MeasureValue'])
n['nd']=n.ResultDetectionConditionText.eq('Not Detected')
k=['OrganizationIdentifier','ActivityIdentifier']
a=n[n.USGSPCode=='00618'].set_index(k);b=n[n.USGSPCode=='71851'].set_index(k)
j=a.join(b,rsuffix='_b',how='inner')
print(len(j),np.nanmax(np.abs(j.v-j.v_b*F)),(j.nd!=j.nd_b).sum(), np.nanmax(np.abs(j.dl-j.dl_b*F)))
print(len(a),len(b),b.index.isin(a.index).all())
t=a.reset_index()
t['nitrate_mg_L_as_N']=t.v
t['detection_limit_mg_L_as_N']=t.dl
t['nondetect']=t.nd
t['well']=t.MonitoringLocationIdentifier
t[['well','ActivityIdentifier','ActivityStartDate','USGSPCode','CharacteristicName','ResultSampleFractionText','nitrate_mg_L_as_N','nondetect','detection_limit_mg_L_as_N','ResultStatusIdentifier']].to_csv('nitrate_as_n.csv',index=False)
print(len(t),t.well.nunique(),t.nd.sum(),len(oth),t.v.isna().sum(),(t.v.isna()&~t.nd).sum())
print(d[(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')&d.USGSPCode.isin(['00620','71850','00630','00631'])].groupby('USGSPCode').size())
j['diff']=j.v-j.v_b*F
print(j['diff'].abs().describe());print(j.loc[j['diff'].abs().nlargest(3).index,['v','v_b']])
r=a[~a.index.isin(b.index)];print(r.nd.sum(),len(r),r.v.describe())
