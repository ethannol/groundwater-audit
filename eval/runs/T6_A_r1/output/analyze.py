import pandas as pd, numpy as np, json
r=pd.read_csv('data/wqp_result.csv')
r['y']=r['ActivityStartDate'].str[:4].astype(int)
c=r[r.MonitoringLocationIdentifier.str.contains('-C')]
e=c[c.y==2005].set_index('MonitoringLocationIdentifier'); l=c[c.y==2018].set_index('MonitoringLocationIdentifier')
for name,sub in [('half',0.5),('full',1.0)]:
    ev=e['ResultMeasureValue'].fillna(e['DetectionQuantitationLimitMeasure/MeasureValue']*sub)
    print(name,ev.median(),l['ResultMeasureValue'].median())
print(r[r.y==2018]['ResultMeasureValue'].median(), (e.ResultMeasureValue.notna()).sum())
