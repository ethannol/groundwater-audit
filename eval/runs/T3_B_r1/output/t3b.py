import pandas as pd, numpy as np
d=pd.read_csv('data/wqp_result.csv',dtype={'USGSPCode':str},low_memory=False)
r=d[(d.USGSPCode=='01000')&(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')].copy()
r['yr']=r.ActivityStartDate.str[:4].astype(int)
r['p']=np.where(r.yr<=2011,'early',np.where(r.yr>=2012,'late',''))
r['v']=r.ResultMeasureValue
r['vf']=r.v.fillna(r['DetectionQuantitationLimitMeasure/MeasureValue']/2)  # sensitivity only
s=r.MonitoringLocationIdentifier
print(r.groupby('p').MonitoringLocationIdentifier.nunique())
both=set(r[r.p=='early'].MonitoringLocationIdentifier)&set(r[r.p=='late'].MonitoringLocationIdentifier)
print('wells in both',len(both))
c=r[s.isin(both)]
w=c.groupby(['MonitoringLocationIdentifier','p']).vf.median().unstack()
print(len(w),w.median(),(w.late>w.early).sum(),(w.late<w.early).sum(),(w.late==w.early).sum())
print(c.groupby('p').agg(n=('v','size'),med=('vf','median'),a10=('v',lambda x:(x>10).sum()/len(x))))
b=c.assign(x=c.v).groupby('p').x.apply(lambda x:(x>10).mean()); print(b)
