import pandas as pd, numpy as np, json
from validators import *
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
n=df[(df.USGSPCode=="00618")&(df.ActivityTypeCode=="Sample-Routine")&(df.ActivityMediaSubdivisionName=="Groundwater")].copy()
print("rows after filter",len(n))
check_unique_key(n,["ResultIdentifier"])
n["year"]=n.ActivityStartDate.str[:4].astype(int)
n["per"]=np.where(n.year.between(2000,2011),"early",np.where(n.year.between(2012,2023),"late",None))
n=n[n.per.notna()].copy()
nd=n.ResultDetectionConditionText!=""
n["hi"]=pd.to_numeric(np.where(nd,n["DetectionQuantitationLimitMeasure/MeasureValue"],n.ResultMeasureValue))
n["lo"]=np.where(nd,0.0,n.hi)
print("nondetect",nd.sum(),"missing hi",n.hi.isna().sum())
n["t"]=n.ActivityStartDate+" "+n["ActivityStartTime/Time"]
site="MonitoringLocationIdentifier"
cohort_composition(n,site,"per")
def pooled(p):
    d=n[n.per==p]
    # median of intervals: report midpoint-free bounds; point = median of detected-or-limit upper bound with lo bound
    return {"n":int(len(d)),"wells":int(d[site].nunique()),"median":float(d.hi.median()),"median_lo":float(d.lo.median()),"nd":int((d.ResultDetectionConditionText!="").sum())}
pe,pl=pooled("early"),pooled("late");print(pe,pl)
last=n.sort_values(["ActivityStartDate","ActivityStartTime/Time"]).groupby([site,"per"]).tail(1)
# check ties on same date/time
tie=n.groupby([site,"per"]).apply(lambda g:(g.t==g.t.max()).sum()>1).sum();print("wells with tied last timestamps",tie)
w=last.pivot(index=site,columns="per",values=["lo","hi"]).dropna()
e_lo,e_hi,l_lo,l_hi=w[("lo","early")],w[("hi","early")],w[("lo","late")],w[("hi","late")]
dec=(l_hi<e_lo);inc=(l_lo>e_hi);ind=~(dec|inc)
sets={p:set(n[n.per==p][site]) for p in("early","late")}
print(len(w),dec.sum(),inc.sum(),ind.sum())
# sensitivity: ties-in-point values; sign test
from scipy.stats import binomtest
bt=binomtest(int(dec.sum()),int(dec.sum()+inc.sum()),0.5).pvalue
rng=np.random.default_rng(1);idx=np.arange(len(w));d=(w[("hi","late")]-w[("hi","early")]).values
bs=[np.median(d[rng.choice(idx,len(idx))]) for _ in range(5000)]
ci=np.percentile(bs,[2.5,97.5]).tolist()
print("sign p",bt,"boot CI median diff",ci,"median diff",np.median(d))
cem,clm=float(e_hi.median()),float(l_hi.median())
print(cem,clm,"nd in cohort",(w[("lo","early")]==0).sum(),(w[("lo","late")]==0).sum())
ans={"pooled_early":{k:pe[k] for k in("n","wells","median")},"pooled_late":{k:pl[k] for k in("n","wells","median")},
"cohort_wells":len(w),"wells_only_early":len(sets["early"]-sets["late"]),"wells_only_late":len(sets["late"]-sets["early"]),
"cohort_early_median":cem,"cohort_late_median":clm,
"cohort_decline":int(dec.sum()),"cohort_increase":int(inc.sum()),"cohort_indeterminate":int(ind.sum()),
"did_nitrate_decline":None,
"notes":"Filter: USGSPCode 00618 (dissolved nitrate, mg/L as N), Sample-Routine, ActivityMediaSubdivision Groundwater; 71851 (asNO3 re-expression), 00631 (nitrate+nitrite), total-fraction codes, QC replicates, leachate/soil-moisture etc excluded. Non-detects handled as intervals [0,DL]; medians use DL as upper bound (<=1 ND shifts only if median is near DL). Cohort last result per period.",
"checks":[f"sign test p={bt:.3g} on decline vs increase wells",f"well-level bootstrap 95% CI of median late-early change (upper-bound values): {ci}",f"wells with tied last timestamps: {int(tie)}","00618 vs 71851 are same measurement in different units; 71851 excluded"],
"caveats":["Pooled sets of wells differ between periods","DLs varied 0.02-0.6 mg/L over time; ND in cohort treated as intervals"]}
json.dump(ans,open("ans_draft.json","w"),indent=1)
print(json.dumps(ans,indent=1)[:600])
