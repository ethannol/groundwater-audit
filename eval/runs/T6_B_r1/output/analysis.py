import pandas as pd, numpy as np, json
from scipy import stats
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
d['y']=d.ActivityStartDate.str[:4]
d['v']=pd.to_numeric(d.ResultMeasureValue.replace('',np.nan))
d['dl']=pd.to_numeric(d['DetectionQuantitationLimitMeasure/MeasureValue'])
d['cens']=d.ResultDetectionConditionText!=''
d['labB']=d.LaboratoryName.str.contains('Lab B')
d['cohort']=d.MonitoringLocationIdentifier.str.startswith('SYN-C')
pd.set_option('display.width',200)
print(d[d.labB][['MonitoringLocationIdentifier','y','v']])
print(d.groupby(['y','cohort','labB']).agg(n=('v','size'),cens=('cens','sum'),med=('v','median'),mn=('v','min'),mx=('v','max')))
print(d[(d.y=='2005')&~d.cens][['MonitoringLocationIdentifier','v']].T)
w=d[d.cohort].pivot(index='MonitoringLocationIdentifier',columns='y',values=['v','cens','dl','labB'])
w.columns=['_'.join(c) for c in w.columns]
print(w.to_string())
late=d[d.y=='2018']; early=d[d.y=='2005']
print('late pooled med',late.v.median(),'cohort late med',late[late.cohort].v.median())
print('late med if LabB were NO3 (/4.427)',pd.concat([late[~late.labB].v,late[late.labB].v/4.427]).median())
print('early med bounds: lower sub 0',np.median(early.v.fillna(0)),'upper sub DL',np.median(early.v.fillna(early.dl)))
print('dup stations', pd.read_csv('data/wqp_station.csv').MonitoringLocationIdentifier.duplicated().sum())
same=(w.v_2005==w.v_2018).sum(); print('identical',same)
