import pandas as pd, numpy as np, json
d=pd.read_csv('data/wqp_result.csv',dtype={'USGSPCode':str},low_memory=False)
a=d[d.USGSPCode=='01000']
r=a[(a.ActivityTypeCode=='Sample-Routine')&(a.ActivityMediaSubdivisionName=='Groundwater')].copy()
print('rows',len(a),'->',len(r))
r['yr']=r.ActivityStartDate.str[:4].astype(int)
r['v']=r.ResultMeasureValue; r['u']=r['ResultMeasure/MeasureUnitCode']
r['dl']=r['DetectionQuantitationLimitMeasure/MeasureValue']; r['dlu']=r['DetectionQuantitationLimitMeasure/MeasureUnitCode']
r['cond']=r.ResultDetectionConditionText
print(r.groupby(['cond','u'],dropna=False).size())
print(r[r.cond.isna()&r.v.isna()].shape, r[r.cond.notna()&r.v.notna()].shape)
print(r[r.cond=='Detected Not Quantified'][['yr','v','dl','dlu']])
print(r.dlu.value_counts(dropna=False))
nd=r[r.cond=='Not Detected']
print(nd.dl.isna().sum(), nd.groupby('yr').dl.agg(['count','min','max']))
det=r[r.cond.isna()]
print(det.groupby('yr').v.agg(['count','min','median','max']))
print('detected with dl>10 or value<dl:',((det.dl>det.v)).sum())
print(r.groupby('yr').dl.agg(['min','max']))
print(r.duplicated(['MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time']).sum())
out={}
for name,(lo,hi) in {'early':(2000,2011),'late':(2012,2023)}.items():
    s=r[(r.yr>=lo)&(r.yr<=hi)]
    ndm=s.cond=='Not Detected'
    dnq=s.cond=='Detected Not Quantified'
    # non-detects with missing limit
    v=s.v.copy()
    lim=s.dl
    lower=v.fillna(0); upper=v.fillna(lim)
    ok=~dnq
    n=int(len(s)); 
    med_lo=np.median(lower[ok]); med_up=np.median(upper[ok])
    # above 10: bounds
    ab_lo=((v>10)).sum()/ok.sum()
    ab_hi=((v>10)|(ndm&(lim>10))).sum()/ok.sum()
    print(name,n,int(ndm.sum()),int(dnq.sum()),'lim',lim[ndm].min(),lim[ndm].max(),'medbounds',med_lo,med_up,'above10',ab_lo,ab_hi,'detmedian',v.median(),'ND share',ndm.mean(), 'maxdet<?', )
    # substitution sensitivity
    half=np.median(v.fillna(lim/2)[ok])
    print(' half-lim sens',half,'nd lim>1:',(lim[ndm]>1).sum(),'n lim values',sorted(lim[ndm].unique())[:20],sorted(lim[ndm].unique())[-5:])
    out[name]=dict(n=n,n_nondetect=int(ndm.sum()),reporting_limit_min=float(lim[ndm].min()),reporting_limit_max=float(lim[ndm].max()),
       median_ugL=float(med_lo) if med_lo==med_up else None,share_above_10_ugL=float(ab_lo) if ab_lo==ab_hi else None,
       median_bounds=[float(med_lo),float(med_up)],share_above_10_bounds=[float(ab_lo),float(ab_hi)],n_detected_not_quantified=int(dnq.sum()))
json.dump(out,open('t3_interim.json','w'),indent=1)
