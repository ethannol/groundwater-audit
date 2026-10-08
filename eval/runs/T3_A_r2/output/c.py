import pandas as pd,numpy as np,json
d=pd.read_csv('data/wqp_result.csv',low_memory=False,dtype={'USGSPCode':str})
d=d[(d.USGSPCode=='01000')&(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')].copy()
d['y']=pd.to_datetime(d.ActivityStartDate).dt.year
d['v']=d.ResultMeasureValue;d['dl']=d['DetectionQuantitationLimitMeasure/MeasureValue']
d['cens']=d.ResultDetectionConditionText.notna()
assert (d.cens==d.v.isna()).all()
out={}
for k,(a,b) in {'early':(2000,2011),'late':(2012,2023)}.items():
    s=d[(d.y>=a)&(d.y<=b)]
    c=s[s.cens];x=s[~s.cens]
    n=len(s)
    # median: censored obs ranked below all detects (limits mostly <= 1-2, median >>) ; check by substitution bounds
    vals=lambda sub:np.median(np.r_[x.v,sub])
    lo=vals(np.zeros(len(c)));hi=vals(c.dl.fillna(0).values)
    med=vals(c.dl.values/2)
    nd_hi=(c.dl>10).sum(); det_gt=(x.v>10).sum()
    print(k,n,len(c),s.dl.min(),s.dl.max(),lo,med,hi,'ND dl>10:',nd_hi,'ND dl range',c.dl.min(),c.dl.max(),'share',det_gt/n,(det_gt+nd_hi)/n, 'dl missing',s.dl.isna().sum(),'det<=10 share lower bound',det_gt/n)
    out[k]=dict(n=n,n_nondetect=len(c),reporting_limit_min=float(c.dl.min()),reporting_limit_max=float(c.dl.max()),median_ugL=round(float(med),3),share_above_10_ugL=round(det_gt/n,4))
    print(c.dl.isna().sum())
json.dump(out,open('tmp.json','w'))
