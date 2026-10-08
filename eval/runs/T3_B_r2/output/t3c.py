import pandas as pd, numpy as np, json
r=pd.read_pickle('/tmp/r.pkl')
r=r[r.period!='out']
out={}
def med(v): return float(np.median(v))
for p,g in r.groupby('period'):
    nd=g[g.ResultDetectionConditionText=='Not Detected']; dnq=g[g.ResultDetectionConditionText=='Detected Not Quantified']
    c=g[g.nd]; det=g[~g.nd]
    lo=np.r_[det.val,np.zeros(len(c))]; hi=np.r_[det.val,c.dl.fillna(0)]
    # Kaplan-Meier style (flip) median for left-censored: ROS-free; use interval bounds
    n=len(g)
    above_lo=(det.val>10).sum()/n
    above_hi=((det.val>10).sum()+(c.dl>10).sum())/n
    out[p]=dict(n=n,n_nondetect=len(nd),n_dnq=len(dnq),n_censored=len(c),
      rl_min=float(c.dl.min()),rl_max=float(c.dl.max()),med_lo=med(lo),med_hi=med(hi),
      share_lo=above_lo,share_hi=above_hi,cens_dl_gt_median=int((c.dl>med(lo)).sum()),
      nd_dl_missing=int(c.dl.isna().sum()),sites=g.MonitoringLocationIdentifier.nunique(),
      detect_median=med(det.val),share_det_only=(det.val>10).sum()/len(det))
    # common reporting cut: censor everything below 1 ug/L
    g2=g.copy(); 
    lo1=np.where(g.nd|(g.val<1),0,g.val); 
    out[p]['med_censored_at_1']=med(np.where(g.nd|(g.val<1),0.0,g.val))
    out[p]['med_censored_at_1_hi']=med(np.where(g.nd|(g.val<1),1.0,g.val))
    out[p]['frac_lt1']=float((g.nd|(g.val<1)).mean())
print(json.dumps(out,indent=1))
s=r.groupby('period').MonitoringLocationIdentifier.agg(set)
com=s['early']&s['late'];print(len(s['early']),len(s['late']),len(com))
c=r[r.MonitoringLocationIdentifier.isin(com)]
for p,g in c.groupby('period'):
    lo=np.where(g.nd,0,g.val);hi=np.where(g.nd,g.dl.fillna(0),g.val)
    print(p,len(g),np.median(lo),np.median(hi),(g.val>10).mean())
json.dump(out,open('/tmp/out.json','w'))
