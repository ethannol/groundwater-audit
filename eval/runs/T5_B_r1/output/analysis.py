import sys; sys.path.insert(0,".")
import json, numpy as np, pandas as pd
from scipy import stats
from validators import *
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
n0=len(df)
a=df[(df.USGSPCode=="01000")&(df.ActivityTypeCode=="Sample-Routine")&(df.ActivityMediaSubdivisionName=="Groundwater")&(df.ActivityMediaName=="Water")].copy()
print("rows all",n0,"filtered",len(a))
checks=[f"rows {n0} -> {len(a)} after code 01000, Sample-Routine, Water/Groundwater"]
a["date"]=pd.to_datetime(a.ActivityStartDate)
a["yr"]=a.date.dt.year
a["val"]=pd.to_numeric(a.ResultMeasureValue.replace("",np.nan))
a["dl"]=pd.to_numeric(a["DetectionQuantitationLimitMeasure/MeasureValue"].replace("",np.nan))
a["cens"]=a.ResultDetectionConditionText!=""
print(a[a.cens&a.dl.isna()].shape, a[(~a.cens)&a.val.isna()].shape)
print(a[a.ResultDetectionConditionText=="Detected Not Quantified"][["val","dl","yr"]])
# unit check
print(a["ResultMeasure/MeasureUnitCode"].value_counts().to_dict(), a["DetectionQuantitationLimitMeasure/MeasureUnitCode"].value_counts().to_dict())
a["lo"]=np.where(a.cens,0.0,a.val); a["hi"]=np.where(a.cens,a.dl,a.val)
assert a.hi.notna().all()
a["period"]=np.where(a.yr.between(2000,2011),"early",np.where(a.yr.between(2012,2023),"late",None))
a=a[a.period.notna()]
# same-day dups
print("same well-date dup rows:",a.duplicated(["MonitoringLocationIdentifier","ActivityStartDate"],keep=False).sum())
a["t"]=pd.to_datetime(a.ActivityStartDate+" "+a["ActivityStartTime/Time"].replace("","00:00:00"))
a=a.sort_values(["MonitoringLocationIdentifier","period","t","ResultIdentifier"])
last=a.groupby(["MonitoringLocationIdentifier","period"]).tail(1)
print(check_unique_key(last,["MonitoringLocationIdentifier","period"]))
checks.append(str(cohort_composition(a,"MonitoringLocationIdentifier","period")))
w=last.pivot(index="MonitoringLocationIdentifier",columns="period",values=["lo","hi","val","cens","yr"])
w=w[w[("hi","early")].notna()&w[("hi","late")].notna()]
print(len(w))
def cls(lo_e,hi_e,lo_l,hi_l):
    if hi_l<lo_e: return "decline"
    if lo_l>hi_e: return "increase"
    return "indeterminate"
w["cls"]=[cls(*r) for r in zip(w[("lo","early")],w[("hi","early")],w[("lo","late")],w[("hi","late")])]
cnt=w.cls.value_counts().to_dict(); print(cnt)
dec,inc,ind=[cnt.get(k,0) for k in("decline","increase","indeterminate")]
n=len(w); det=dec+inc
cp=stats.binomtest(dec,det).proportion_ci(0.95,method="exact")
p=stats.binomtest(dec,det,0.5).pvalue
both=w[(~w[("cens","early")].astype(bool))&(~w[("cens","late")].astype(bool))]
ratio=(both[("val","late")]/both[("val","early")])
med=float(ratio.median()); print("both detected",len(both),med)
# bootstrap CI for median ratio (well resampling)
rng=np.random.default_rng(1); r=ratio.values
bs=[np.median(rng.choice(r,len(r))) for _ in range(5000)]; mci=np.percentile(bs,[2.5,97.5])
# substitution sensitivity
sens={}
for nm,f in {"zero":0,"half":.5,"full":1}.items():
    def v(per):
        return np.where(w[("cens",per)].astype(bool),f*w[("hi",per)],w[("val",per)]).astype(float)
    e,l=v("early"),v("late"); sens[nm]=(int((l<e).sum()),int((l>e).sum()),int((l==e).sum()))
print(sens)
# determinate-only sensitivity: exclude wells with a non-detect
nd=w[(w[("cens","early")].astype(bool))|(w[("cens","late")].astype(bool))]
print("wells w/ ND",len(nd), nd.cls.value_counts().to_dict())
# gap between last-dates
print(w[("yr","early")].astype(int).describe(), w[("yr","late")].astype(int).describe())
# tolerance sensitivity: require >=20% change
def tol(r):
    return "decline" if r[("hi","late")]<0.8*r[("lo","early")] else "increase" if r[("lo","late")]>1.25*r[("hi","early")] else "indeterminate"
t=w.apply(tol,axis=1).value_counts().to_dict(); print("20% tol",t)
share_all=dec/n
print(dec,inc,ind,n,dec/det,cp,p,share_all)
out=dict(cohort_wells=n,decline=dec,increase=inc,indeterminate=ind,
 share_declining=round(dec/det,3),share_declining_denominator="determinate wells",
 share_declining_ci95=[round(cp.low,3),round(cp.high,3)],
 ci_method="Exact Clopper-Pearson binomial interval on well-level directions among determinate wells (wells independent, one last result per well per period)",
 sign_test_p=float(p),
 median_ratio_late_over_early_both_detected=round(med,3),
 independent_unit="The well (monitoring location): one last routine result per well per period, so repeated and temporally close samples within a well are collapsed. Wells are treated as independent although neighbouring wells share aquifers and USGS programs (spatial dependence not modelled).",
 nondetect_sensitivity=f"Substitution used only as a labelled sensitivity check (decline/increase/tie): zero {sens['zero']}, half-limit {sens['half']}, full-limit {sens['full']}. Direction (more declines than increases or not) per substitution: "+", ".join(f"{k}: {'declines>increases' if v[0]>v[1] else 'increases>=declines'}" for k,v in sens.items())+". Primary classification uses intervals [0,DL] for non-detects.",
 notes=f"Share declining among all cohort wells = {share_all:.3f} ({dec}/{n}); {ind} wells indeterminate and not counted as either direction. Median ratio over {len(both)} both-detected wells, well-bootstrap 95% CI [{mci[0]:.2f},{mci[1]:.2f}]. Reporting limits varied 0.09-20 ug/L over time; the 2012 limit of 20 ug/L is elevated. Last-result sample dates differ by well, so the interval between paired results varies. A 20%-change tolerance variant gives {t}.",
 checks=checks+[f"cohort composition: {len(w)} wells in both periods","excluded QC replicates, 'Not determined' activity types, non-groundwater subdivisions (elutriation, soil moisture, interstitial, leachate) and total As (01002)","unit: all ug/l; no re-expressed pairs for As (single parameter code)", "no duplicate (well,period) keys after last-result selection"],
 caveats=["Wells selected for repeat sampling are not a random sample of the county","Mixed methods/labs across periods","Preliminary results included","Spatial dependence between wells not modelled","Detected values treated as exact; analytical error ignored"])
json.dump(out,open("answer.json","w"),indent=1,default=float)
