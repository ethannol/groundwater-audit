import pandas as pd, numpy as np, json
from scipy import stats
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
n0=len(df)
a=df[(df.USGSPCode=="01000")&(df.ActivityTypeCode=="Sample-Routine")&(df.ActivityMediaSubdivisionName=="Groundwater")].copy()
print("rows all",n0,"filtered",len(a))
a["date"]=pd.to_datetime(a.ActivityStartDate); a["yr"]=a.date.dt.year
cens=a.ResultDetectionConditionText!=""
lim=pd.to_numeric(a["DetectionQuantitationLimitMeasure/MeasureValue"])
val=pd.to_numeric(a.ResultMeasureValue)
a["lo"]=np.where(cens,0,val); a["hi"]=np.where(cens,lim,val); a["cens"]=cens
assert a[["lo","hi"]].notna().all().all()
a["period"]=np.where(a.yr<=2011,"early",np.where(a.yr>=2012,"late",None))
a=a[a.yr.between(2000,2023)]
a["t"]=a["ActivityStartTime/Time"]
a=a.sort_values(["MonitoringLocationIdentifier","date","t","ResultIdentifier"])
print("dup well/date/time:",a.duplicated(["MonitoringLocationIdentifier","date","t"],keep=False).sum())
last=a.groupby(["MonitoringLocationIdentifier","period"]).tail(1)
w=last.pivot(index="MonitoringLocationIdentifier",columns="period",values=["lo","hi","cens"]).dropna()
print("wells with early",a[a.period=="early"].MonitoringLocationIdentifier.nunique(),"late",a[a.period=="late"].MonitoringLocationIdentifier.nunique(),"cohort",len(w))
def cls(lo1,hi1,lo2,hi2):
    if hi2<lo1: return "decline"
    if lo2>hi1: return "increase"
    return "indeterminate"
w["cls"]=[cls(*r) for r in zip(w[("lo","early")],w[("hi","early")],w[("lo","late")],w[("hi","late")])]
cnt=w.cls.value_counts(); print(cnt)
dec,inc,ind=[int(cnt.get(k,0)) for k in("decline","increase","indeterminate")]
N=len(w); det=dec+inc
# sub sensitivity
sens={}
for name,f in [("zero",0),("half",.5),("full",1)]:
    e=np.where(w[("cens","early")].astype(bool),w[("hi","early")]*f,w[("lo","early")])
    l=np.where(w[("cens","late")].astype(bool),w[("hi","late")]*f,w[("lo","late")])
    sens[name]=dict(decline=int((l<e).sum()),increase=int((l>e).sum()),tie=int((l==e).sum()),median_ratio=float(np.median(l[e>0]/e[e>0])) if True else None)
print(sens)
# well-level bootstrap
rng=np.random.default_rng(1); c=np.asarray(w.cls.astype(object))
B=20000; idx=rng.integers(0,N,(B,N)); sh_all=(c[idx]=="decline").mean(1)
ci_all=np.percentile(sh_all,[2.5,97.5])
cp=stats.binomtest(dec,N).proportion_ci(method="exact")
cpd=stats.binomtest(dec,det).proportion_ci(method="exact")
p=stats.binomtest(dec,det,0.5).pvalue
both=(~w[("cens","early")].astype(bool))&(~w[("cens","late")].astype(bool))
ratio=w.loc[both,("lo","late")]/w.loc[both,("lo","early")]
mr=float(np.median(ratio)); 
bm=[np.median(rng.choice(ratio.values,len(ratio))) for _ in range(5000)]
print("both detected",both.sum(),mr,np.percentile(bm,[2.5,97.5]))
print("share all",dec/N,ci_all,cp,"share det",dec/det,cpd,"p",p)
# limits in cohort
print(w[("cens","early")].sum(),w[("cens","late")].sum())
print(a.groupby("period").agg(n=("lo","size"),wells=("MonitoringLocationIdentifier","nunique"),cens=("cens","mean")))
out=dict(cohort_wells=int(N),decline=dec,increase=inc,indeterminate=ind,
 share_declining=round(dec/det,4),share_declining_denominator="determinate wells",
 share_declining_ci95=[round(cpd.low,4),round(cpd.high,4)],
 ci_method="Exact Clopper-Pearson binomial 95% interval on declining wells among determinate wells, treating wells as independent units",
 sign_test_p=float(p),
 median_ratio_late_over_early_both_detected=round(mr,4),
 independent_unit="The well: one last-in-period result per well per period; repeated samples within a well and nearby wells (shared aquifer, lab, method changes) are not independent, so intervals are likely too narrow.",
 nondetect_sensitivity="",notes="",checks=[],caveats=[])
out["_extra"]=dict(sens=sens,ci_all=[float(x) for x in ci_all],cp_all=[cp.low,cp.high],ratio_ci=[float(x) for x in np.percentile(bm,[2.5,97.5])],both=int(both.sum()),share_all=dec/N)
json.dump(out,open("tmp_out.json","w"),indent=1,default=float)
