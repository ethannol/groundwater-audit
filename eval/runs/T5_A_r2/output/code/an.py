import pandas as pd, numpy as np, json
from scipy import stats
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
a=d[(d.USGSPCode.astype(str).str.zfill(5)=='01000')&(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')].copy()
print(len(a), a['ResultMeasure/MeasureUnitCode'].value_counts(dropna=False).to_dict())
a['dt']=pd.to_datetime(a.ActivityStartDate)
a['yr']=a.dt.dt.year
a=a[(a.yr>=2000)&(a.yr<=2023)]
a['per']=np.where(a.yr<=2011,'early','late')
a['dl']=a['DetectionQuantitationLimitMeasure/MeasureValue']
a['nd']=a.ResultMeasureValue.isna()
print('nd without dl',(a.nd&a.dl.isna()).sum())
a['t']=a['ActivityStartTime/Time'].fillna('')
a=a.sort_values(['MonitoringLocationIdentifier','dt','t'])
# same-day ties
tie=a.groupby(['MonitoringLocationIdentifier','per']).apply(lambda g:(g.dt==g.dt.max()).sum()>1)
print('wells with tied last date',tie.sum())
last=a.groupby(['MonitoringLocationIdentifier','per']).tail(1)
w=last.pivot(index='MonitoringLocationIdentifier',columns='per',values=['ResultMeasureValue','dl','nd']).dropna(subset=[('nd','early'),('nd','late')])
print(len(w))
def iv(v,dl,nd,mode='int'):
    if nd: return (0,dl) if mode=='int' else None
    return (v,v)
def classify(w,sub=None):
    out=[]
    for _,r in w.iterrows():
        res=[]
        for p in ['early','late']:
            v,dl,nd=r[('ResultMeasureValue',p)],r[('dl',p)],r[('nd',p)]
            if nd:
                s={'zero':0,'half':dl/2,'full':dl}[sub] if sub else None
                res.append((0,dl) if not sub else (s,s))
            else: res.append((v,v))
        e,l=res
        if l[1]<e[0]: out.append('decline')
        elif l[0]>e[1]: out.append('increase')
        else: out.append('indeterminate')
    return pd.Series(out,index=w.index)
c=classify(w); vc=c.value_counts(); print(vc.to_dict())
for s in ['zero','half','full']:
    cc=classify(w,s); print(s,cc.value_counts().to_dict())
dec,inc,ind=[int(vc.get(k,0)) for k in ['decline','increase','indeterminate']]
n=dec+inc
cp=stats.binomtest(dec,n).proportion_ci(0.95,method='exact')
p=stats.binomtest(dec,n,0.5).pvalue
both=w[(~w[('nd','early')].astype(bool))&(~w[('nd','late')].astype(bool))]
ratio=(both[('ResultMeasureValue','late')]/both[('ResultMeasureValue','early')])
print(len(both),ratio.median(),dec,inc,ind,dec/n,cp,p, dec/len(w))
# spatial clustering: distinct stations coords rounding
st=pd.read_csv('data/wqp_station.csv').set_index('MonitoringLocationIdentifier')
ll=st.loc[w.index,['LatitudeMeasure','LongitudeMeasure']].round(2).drop_duplicates()
print('0.01deg cells',len(ll))
print('nd counts', w[('nd','early')].sum(), w[('nd','late')].sum())
json.dump(dict(dec=dec,inc=inc,ind=ind,n=len(w),share=dec/n,ci=[cp.low,cp.high],p=p,ratio=float(ratio.median()),nboth=len(both),
  sens={s:classify(w,s).value_counts().to_dict() for s in ['zero','half','full']}),open('code/res.json','w'),default=int)
