import pandas as pd, numpy as np, json
from validators import *
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
F=14.0067/62.0049
n=df[df.CharacteristicName.isin(["Nitrate","Inorganic nitrogen (nitrate and nitrite)"])]
print("nitrate-ish rows",len(n))
r=n[(n.ActivityTypeCode=="Sample-Routine")&(n.ActivityMediaSubdivisionName=="Groundwater")]
print("routine GW",len(r))
print(r.groupby(["USGSPCode","ResultSampleFractionText"]).size())
oth=r[(r.CharacteristicName=="Nitrate")&(r.ResultSampleFractionText!="Dissolved")]
print("other fraction nitrate",len(oth), "all-char other fraction",len(r[r.ResultSampleFractionText!="Dissolved"]))
d=r[(r.CharacteristicName=="Nitrate")&(r.ResultSampleFractionText=="Dissolved")].copy()
print(d.groupby(["USGSPCode","ResultMeasure/MeasureUnitCode","ResultDetectionConditionText"]).size())
key=["MonitoringLocationIdentifier","ActivityIdentifier"]
d["act"]=d.ActivityStartDate+"|"+d.ActivityStartTime_ if False else d.ActivityStartDate
check_unique_key(d[d.USGSPCode=="00618"],key); check_unique_key(d[d.USGSPCode=="71851"],key)
check_reexpressed_pairs(d,key)
# pair check
a=d[d.USGSPCode=="00618"].set_index(key); b=d[d.USGSPCode=="71851"].set_index(key)
j=a.join(b,lsuffix="_a",rsuffix="_b",how="inner")
print("activities with both",len(j))
va=pd.to_numeric(j.ResultMeasureValue_a.replace("",np.nan));vb=pd.to_numeric(j.ResultMeasureValue_b.replace("",np.nan))
print((va/vb).describe()); print("ND both", ((j.ResultDetectionConditionText_a!="")&(j.ResultDetectionConditionText_b!="")).sum(), "ND mismatch",((j.ResultDetectionConditionText_a!="")!=(j.ResultDetectionConditionText_b!="")).sum())
only_b=b.index.difference(a.index); print("71851 without 00618",len(only_b))
dropped=d[(d.USGSPCode=="71851")&d.set_index(key).index.isin(a.index)]
print("dropped",len(dropped))
keep=pd.concat([d[d.USGSPCode=="00618"],d[(d.USGSPCode=="71851")&~d.set_index(key).index.isin(a.index)]])
keep=keep.copy()
v=pd.to_numeric(keep.ResultMeasureValue.replace("",np.nan))
dl=pd.to_numeric(keep["DetectionQuantitationLimitMeasure/MeasureValue"].replace("",np.nan))
isno3=keep["ResultMeasure/MeasureUnitCode"]=="mg/l asNO3"
f=np.where(isno3,F,1.0)
keep["value_mgL_as_N"]=v*f; keep["detection_limit_mgL_as_N"]=dl*f
keep["censored"]=keep.ResultDetectionConditionText!=""
keep["original_unit"]=keep["ResultMeasure/MeasureUnitCode"]
print("censored w/ value",(keep.censored&v.notna()).sum(),"uncensored w/o value",(~keep.censored&v.isna()).sum())
print("dup keys after",keep.duplicated(key).sum())
keep["site"]=keep.MonitoringLocationIdentifier
cols=["MonitoringLocationIdentifier","ActivityIdentifier","ActivityStartDate","USGSPCode","CharacteristicName","ResultSampleFractionText","original_unit","ResultMeasureValue","value_mgL_as_N","censored","detection_limit_mgL_as_N","ResultAnalyticalMethod/MethodIdentifier","LaboratoryName"]
keep[cols].to_csv("nitrate_as_n.csv",index=False)
rows=len(keep);wells=keep.MonitoringLocationIdentifier.nunique();nd=int(keep.censored.sum())
print(rows,wells,nd)
other=r[(r.ResultSampleFractionText!="Dissolved")]
print(other.groupby(["CharacteristicName","USGSPCode"]).size())
ex={"00620":"Nitrate, Total fraction (unfiltered): different fraction from dissolved",
"71850":"Nitrate, Total fraction, reported as NO3: different fraction and unit-expressed",
"00630":"Nitrate+nitrite, Total: different chemical definition and fraction",
"00631":"Nitrate+nitrite, Dissolved: different chemical definition (includes nitrite)",
"71851":"Included only where no 00618 in same activity; otherwise dropped as re-expression of 00618 (mg/L as NO3)"}
ans={"rows_in_table":rows,"wells_in_table":wells,"nondetect_rows_in_table":nd,
"pcodes_included":["00618","71851"],"pcodes_excluded":{k:v for k,v in ex.items() if k!="71851"},
"unit_conversion_factors_used":{"mg/l as N -> mg/l as N":1.0,"mg/l asNO3 -> mg/l as N":round(F,5)},
"rows_dropped_as_same_measurement_reexpressed":len(dropped),
"rows_excluded_other_fraction":int(len(other[other.CharacteristicName=="Nitrate"])),
"nitrate_plus_nitrite_combined":False,
"notes":"Filters: Sample-Routine, ActivityMediaSubdivisionName=Groundwater (excluded leachate, elutriation, soil moisture, interstitial, bulk deposition), CharacteristicName=Nitrate, Dissolved. 71851 (NO3) is the same measurement as 00618 re-expressed; 71851 rows dropped where the same activity has 00618; factor 14.0067/62.0049. QC replicates, reference material and 'Not determined' activity types excluded. Non-detects kept with censored flag and limit in mg/L as N; no substitution. Total-fraction nitrate rows counted in rows_excluded_other_fraction (nitrate char only, routine groundwater); 00630 rows (nitrate+nitrite total) not included in that count.",
"checks":["unique (site,activity) key after filtering","pair ratio 00618/71851 checked ~ conversion factor"],"caveats":["Preliminary/historical status not filtered"]}
json.dump(ans,open("answer.json","w"),indent=1)
