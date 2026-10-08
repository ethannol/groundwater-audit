import pandas as pd, numpy as np, json
from scipy import stats
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
a=d[(d.USGSPCode.astype(str).str.zfill(5)=='01000')&(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')].copy()
print(len(a), a['ResultMeasure/MeasureUnitCode'].value_counts(dropna=False).to_dict())
a['dt']=pd.to_datetime(a.ActivityStartDate)
a['t']=a['ActivityStartTime/Time'].fillna('')
dl=a['DetectionQuantitationLimitMeasure/MeasureValue']
a['nd']=a.ResultDetectionConditionText.eq('Not Detected')
dnq=a.ResultDetectionConditionText.eq('Detected Not Quantified')
print('DNQ',dnq.sum(),'ND no DL',(a.nd&dl.isna()).sum(),'ND with value',(a.nd&a.ResultMeasureValue.notna()).sum(), 'det no val',(~a.nd&~dnq&a.ResultMeasureValue.isna()).sum())
a=a[~dnq&~(a.nd&dl.isna())]
dl=a['DetectionQuantitationLimitMeasure/MeasureValue']
a['lo']=np.where(a.nd,0,a.ResultMeasureValue); a['hi']=np.where(a.nd,dl,a.ResultMeasureValue)
a['dlv']=dl
a['p']=np.where(a.dt.dt.year.between(2000,2011),'e',np.where(a.dt.dt.year.between(2012,2023),'l',None))
a=a[a.p.notna()]
a=a.sort_values(['dt','t','ResultIdentifier'])
last=a.groupby(['MonitoringLocationIdentifier','p']).tail(1)
w=last.pivot(index='MonitoringLocationIdentifier',columns='p',values=['lo','hi','nd','ResultMeasureValue','dlv']).dropna(subset=[('lo','e'),('lo','l')])
print(len(w))
def cls(r):
    if r[('hi','l')]<r[('lo','e')]: return 'decline'
    if r[('lo','l')]>r[('hi','e')]: return 'increase'
    return 'indet'
w['c']=w.apply(cls,axis=1); print(w.c.value_counts())
n=len(w);k=(w.c=='decline').sum();i=(w.c=='increase').sum();m=k+i
print('nd pairs',(w[('nd','e')]|w[('nd','l')]).sum())
from scipy.stats import beta, binomtest
ci=binomtest(int(k),int(m)).proportion_ci(0.95,method='exact'); print(k,i,m,k/m,ci)
p=binomtest(int(k),int(m),0.5).pvalue; print(p)
w=w.astype({('nd','e'):bool,('nd','l'):bool,('ResultMeasureValue','e'):float,('ResultMeasureValue','l'):float,('dlv','e'):float,('dlv','l'):float})
bd=w[~w[('nd','e')]&~w[('nd','l')]]
rat=(bd[('ResultMeasureValue','l')]/bd[('ResultMeasureValue','e')]); rat=rat[np.isfinite(rat)&(rat>0)]
print(len(bd),rat.median())
# sensitivity
for name,f in [('zero',0),('half',.5),('full',1)]:
    e=np.where(w[('nd','e')],w[('dlv','e')]*f,w[('ResultMeasureValue','e')]);l=np.where(w[('nd','l')],w[('dlv','l')]*f,w[('ResultMeasureValue','l')])
    print(name,(l<e).sum(),(l>e).sum(),(l==e).sum(),np.median(l/np.where(e>0,e,np.nan)) if True else 0)
# spatial clustering
st=pd.read_csv('data/wqp_station.csv').set_index('MonitoringLocationIdentifier')
w['huc']=st.reindex(w.index)['HUCEightDigitCode'].values
print(w.huc.value_counts().head(), pd.crosstab(w.huc,w.c))
print(a.groupby('MonitoringLocationIdentifier').size().describe())
w.to_csv('cohort.csv')
