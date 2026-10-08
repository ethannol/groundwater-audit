import pandas as pd, numpy as np, json
r=pd.read_csv('data/wqp_result.csv',low_memory=False,dtype={'USGSPCode':str})
n=r[(r.USGSPCode=='00618')&(r.ActivityTypeCode=='Sample-Routine')&(r.ActivityMediaSubdivisionName=='Groundwater')].copy()
n['site']=n.MonitoringLocationIdentifier
n['dt']=pd.to_datetime(n.ActivityStartDate+' '+n['ActivityStartTime/Time'].fillna('00:00:00'))
n['nd']=n.ResultDetectionConditionText.eq('Not Detected')
dl=n['DetectionQuantitationLimitMeasure/MeasureValue']
print('nd missing DL',(n.nd&dl.isna()).sum(),'detect missing value',(~n.nd&n.ResultMeasureValue.isna()).sum(), n['DetectionQuantitationLimitMeasure/MeasureUnitCode'].value_counts().to_dict())
n['lo']=np.where(n.nd,0,n.ResultMeasureValue); n['hi']=np.where(n.nd,dl,n.ResultMeasureValue)
n['val']=n.hi  # NDs at DL for medians
y=n.dt.dt.year
n['per']=np.where(y.between(2000,2011),'early',np.where(y.between(2012,2023),'late',None))
n=n[n.per.notna()]
out={}
for p in['early','late']:
    d=n[n.per==p]; out['pooled_'+p]={'n':int(len(d)),'wells':int(d.site.nunique()),'median':float(d.val.median())}
    print(p,'nd',d.nd.sum(),'median with ND=DL/2',np.median(np.where(d.nd,d.hi/2,d.val)),'ND=0',np.median(np.where(d.nd,0,d.val)))
E_=set(n[n.per=='early'].site);L=set(n[n.per=='late'].site);C=E_&L
out['cohort_wells']=len(C);out['wells_only_early']=len(E_-L);out['wells_only_late']=len(L-E_)
last=n.sort_values('dt').groupby(['site','per']).tail(1)
print('ties same-day check', n.groupby(['site','ActivityStartDate','per']).size().gt(1).sum())
a=last[(last.per=='early')&last.site.isin(C)].set_index('site').sort_index()
b=last[(last.per=='late')&last.site.isin(C)].set_index('site').sort_index()
out['cohort_early_median']=float(a.val.median());out['cohort_late_median']=float(b.val.median())
dec=inc=ind=0
for s in a.index:
    x,z=a.loc[s],b.loc[s]
    if z.hi<x.lo: dec+=1
    elif z.lo>x.hi: inc+=1
    else: ind+=1
out.update(cohort_decline=dec,cohort_increase=inc,cohort_indeterminate=ind)
print(out, 'cohort NDs',a.nd.sum(),b.nd.sum())
d=(b.val-a.val); print('median diff',d.median(), 'paired wilcoxon');
from scipy.stats import wilcoxon; print(wilcoxon(b.val,a.val))
json.dump(out,open('/tmp/o.json','w'))
