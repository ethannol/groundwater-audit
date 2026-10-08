import sys; sys.path.insert(0,"/Users/ethannol/.cache/gwaudit/gwaudit_T4_B_r2_ufc5eqlh/work")
import pandas as pd, numpy as np, json
import validators as v
d=pd.read_csv('data/wqp_result.csv',low_memory=False,dtype={'USGSPCode':str})
print(d.USGSPCode.unique())
n=d[d.USGSPCode.astype(str).str.zfill(5)=='00618'].copy()
print(len(n)); 
for c in ['ActivityTypeCode','ActivityMediaSubdivisionName','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','DetectionQuantitationLimitMeasure/MeasureUnitCode','ResultStatusIdentifier','ResultValueTypeName']:
    print(n[c].value_counts(dropna=False).to_dict())
r=n[(n.ActivityTypeCode=='Sample-Routine')&(n.ActivityMediaSubdivisionName=='Groundwater')].copy()
print('routine gw',len(r))
v.check_unique_key(r,['MonitoringLocationIdentifier','ActivityIdentifier','ResultIdentifier'])
v.check_unique_key(r,['MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time'])
r['date']=pd.to_datetime(r.ActivityStartDate)
r['nd']=r.ResultDetectionConditionText.eq('Not Detected')
r['val']=pd.to_numeric(r.ResultMeasureValue)
r['dl']=pd.to_numeric(r['DetectionQuantitationLimitMeasure/MeasureValue'])
# unit check for ND DLs
print(r[r.nd]['DetectionQuantitationLimitMeasure/MeasureUnitCode'].value_counts(dropna=False))
print('ND w/o DL',(r.nd&r.dl.isna()).sum(),'detect w/o val',(~r.nd&r.val.isna()).sum())
print('detected with unit not mg/l as N',(~r.nd&(r['ResultMeasure/MeasureUnitCode']!='mg/l as N')).sum())
# convert DL if in NO3: N = NO3*14.007/62.004
f=14.007/62.004
mask=r['DetectionQuantitationLimitMeasure/MeasureUnitCode'].eq('mg/l asNO3')
r.loc[mask,'dl']*=f
r['hi']=np.where(r.nd,r.dl,r.val); r['lo']=np.where(r.nd,0.0,r.val)
r['year']=r.date.dt.year
r=r[(r.year>=2000)&(r.year<=2023)]
r['period']=np.where(r.year<=2011,'early','late')
v.censoring_profile(r.assign(ResultDetectionConditionText=r.ResultDetectionConditionText.fillna('')).rename(columns={}),by=('period',))
print(r.groupby('period').apply(lambda g: pd.Series({'nd':g.nd.sum(),'dlmax':g.dl.max()})))
print(r[r.nd].groupby('year').dl.agg(['count','min','max']))
# same-day multiples per well
print('wells-day dup',r.duplicated(['MonitoringLocationIdentifier','ActivityStartDate']).sum())
cm=v.cohort_composition(r,'MonitoringLocationIdentifier','period')
def med_interval(g):
    # median of intervals: bounds; point estimate using midpoint-free: lo/hi medians
    return float(np.median(g.lo)),float(np.median(g.hi))
out={}
for p in ['early','late']:
    g=r[r.period==p]
    print(p,len(g),g.MonitoringLocationIdentifier.nunique(),'median lo/hi',med_interval(g),'nd',g.nd.sum())
    out[p]=(len(g),g.MonitoringLocationIdentifier.nunique(),med_interval(g))
# last result per well-period (latest date; ties -> time, then max? check)
r=r.sort_values(['MonitoringLocationIdentifier','date','ActivityStartTime/Time'])
last=r.groupby(['MonitoringLocationIdentifier','period']).tail(1)
print('ties on last date:',r.groupby(['MonitoringLocationIdentifier','period']).date.apply(lambda s:(s==s.max()).sum()>1).sum())
w=last.pivot(index='MonitoringLocationIdentifier',columns='period',values=['lo','hi','nd'])
coh=w.dropna()
print('cohort',len(coh))
el,eh,ll,lh=coh[('lo','early')],coh[('hi','early')],coh[('lo','late')],coh[('hi','late')]
dec=(lh<el); inc=(ll>eh); ind=~(dec|inc)
print('decline',dec.sum(),'increase',inc.sum(),'indet',ind.sum())
# sensitivity point comparison among detects
print('cohort ND early',coh[('nd','early')].sum(),'late',coh[('nd','late')].sum())
print('cohort medians lo/hi early',el.median(),eh.median(),'late',ll.median(),lh.median())
from scipy.stats import binomtest
k=dec.sum()+inc.sum()
print('sign test p',binomtest(int(dec.sum()),int(k),0.5).pvalue if k else None)
rng=np.random.default_rng(1)
diffs=[]
a=np.c_[el,eh,ll,lh]
for _ in range(5000):
    s=a[rng.integers(0,len(a),len(a))]
    diffs.append(np.median(s[:,3])-np.median(s[:,1]))
print('boot cohort median diff (late hi - early hi) CI',np.percentile(diffs,[2.5,97.5]))
# pooled bootstrap by well
wells=r.MonitoringLocationIdentifier.unique()
gb={k:g for k,g in r.groupby('MonitoringLocationIdentifier')}
pd_=[]
for _ in range(1000):
    ws=rng.choice(wells,len(wells))
    s=pd.concat([gb[x] for x in ws])
    pd_.append(s[s.period=='late'].hi.median()-s[s.period=='early'].hi.median())
print('pooled boot diff CI',np.percentile(pd_,[2.5,97.5]))
