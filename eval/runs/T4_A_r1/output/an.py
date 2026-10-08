import pandas as pd, numpy as np, json
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
n=d[(d.USGSPCode.astype(str).str.zfill(5)=='00618')&(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')].copy()
print(len(n), n['ResultMeasure/MeasureUnitCode'].value_counts(dropna=False).to_dict())
n['nd']=n.ResultDetectionConditionText.eq('Not Detected')
n['dl']=n['DetectionQuantitationLimitMeasure/MeasureValue']
print('nd w/o dl',(n.nd&n.dl.isna()).sum(),'nondetect with value',(n.nd&n.ResultMeasureValue.notna()).sum(),'detect no value',(~n.nd&n.ResultMeasureValue.isna()).sum())
n['dt']=pd.to_datetime(n.ActivityStartDate); n['y']=n.dt.dt.year
n['lo']=np.where(n.nd,0,n.ResultMeasureValue); n['hi']=np.where(n.nd,n.dl,n.ResultMeasureValue)
n['v']=np.where(n.nd,n.dl,n.ResultMeasureValue)  # ND at DL for medians
n=n[n.y.between(2000,2023)]
n['p']=np.where(n.y<=2011,'e','l')
w='MonitoringLocationIdentifier'
res={}
for p,k in(('e','pooled_early'),('l','pooled_late')):
    s=n[n.p==p]; res[k]={'n':len(s),'wells':s[w].nunique(),'median':float(s.v.median())}
E=set(n[n.p=='e'][w]);L=set(n[n.p=='l'][w]);C=E&L
res['cohort_wells']=len(C);res['wells_only_early']=len(E-L);res['wells_only_late']=len(L-E)
n=n.sort_values([w,'dt','ActivityStartTime/Time'],na_position='first')
last=n[n[w].isin(C)].groupby([w,'p']).tail(1)
# same-day ties
print('ties',n[n[w].isin(C)].groupby([w,'p','dt']).size().gt(1).sum())
a=last[last.p=='e'].set_index(w);b=last[last.p=='l'].set_index(w).loc[a.index]
res['cohort_early_median']=float(a.v.median());res['cohort_late_median']=float(b.v.median())
dec=inc=ind=0
for i in a.index:
    if b.lo[i]>a.hi[i]: inc+=1
    elif b.hi[i]<a.lo[i]: dec+=1
    else: ind+=1
res.update(cohort_decline=dec,cohort_increase=inc,cohort_indeterminate=ind)
print(res)
print((b.v-a.v).describe(), (a.nd.sum(),b.nd.sum()))
json.dump(res,open('res_tmp.json','w'))
