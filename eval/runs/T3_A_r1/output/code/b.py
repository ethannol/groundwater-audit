import pandas as pd, numpy as np, json
d=pd.read_csv('data/wqp_result.csv',dtype=str)
d=d[(d.USGSPCode=='01000')&(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')].copy()
print(len(d), d['ResultMeasure/MeasureUnitCode'].value_counts(dropna=False).to_dict())
d['y']=d.ActivityStartDate.str[:4].astype(int)
d['v']=pd.to_numeric(d.ResultMeasureValue)
d['dl']=pd.to_numeric(d['DetectionQuantitationLimitMeasure/MeasureValue'])
d['cens']=d.v.isna()
print(d[d.cens].ResultDetectionConditionText.value_counts(), d[d.cens].dl.isna().sum(), (d.v<=0).sum())
print(d[~d.cens].dl.describe())
out={}
for k,(a,b) in {'early':(2000,2011),'late':(2012,2023)}.items():
    s=d[(d.y>=a)&(d.y<=b)]; c=s[s.cens]; q=s[~s.cens]
    n=len(s); nd=len(c)
    # rl: all reported limits (censored records)
    rl=c.dl
    # bounds: substitution 0 and substitution at DL
    lo=np.where(s.cens,0,s.v); hi=np.where(s.cens,s.dl,s.v)
    ab=(q.v>10).sum(); amb=(c.dl>10).sum()
    # median: determinable if censored values all below median
    med=np.median(lo),np.median(hi)
    # simple: sort with censored as < DL; median is identifiable if rank-median value > max dl of censored below
    print(k,n,nd,rl.min(),rl.max(),'med bounds',med,'above10 detected',ab,'cens w DL>10',amb,'share',ab/n,(ab+amb)/n,'min detected',q.v.min(), 'dl>med',(c.dl>med[0]).sum())
    print(c.dl.describe()[['min','50%','max']].to_dict(), (q.v<q.dl).sum() if q.dl.notna().any() else '')
    out[k]=dict(n=n,nd=nd,min=rl.min(),max=rl.max(),med=med,ab=ab,amb=amb)
print('----')
for k,(a,b) in {'early':(2000,2011),'late':(2012,2023)}.items():
    s=d[(d.y>=a)&(d.y<=b)&d.cens]
    n=s[s.ResultDetectionConditionText=='Not Detected']
    print(k,len(n),n.dl.min(),n.dl.max(),(s.ResultDetectionConditionText!='Not Detected').sum(), s.dl.min(), s.dl.max())
