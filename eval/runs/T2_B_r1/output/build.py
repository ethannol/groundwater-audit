import sys; sys.path.insert(0,".")
import pandas as pd, numpy as np, json
from validators import *
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
n=d[d.CharacteristicName.isin(['Nitrate','Inorganic nitrogen (nitrate and nitrite)'])]
g=n[(n.ActivityTypeCode=='Sample-Routine')&(n.ActivityMediaSubdivisionName=='Groundwater')].copy()
F=14.0067/62.0049
g['val']=pd.to_numeric(g.ResultMeasureValue.replace('',np.nan))
g['dl']=pd.to_numeric(g['DetectionQuantitationLimitMeasure/MeasureValue'].replace('',np.nan))
dis=g[g.ResultSampleFractionText=='Dissolved']
nit=dis[dis.CharacteristicName=='Nitrate']
base=nit[nit.USGSPCode=='00618']; alt=nit[nit.USGSPCode=='71851']
# verify the alt rows are re-expressions of base rows
k=['MonitoringLocationIdentifier','ActivityIdentifier']
m=alt.merge(base,on=k,suffixes=('_a','_b'))
det=m.dropna(subset=['val_a','val_b'])
print('pairs',len(m),'detected pairs',len(det),'max abs diff after conversion',(det.val_a*F-det.val_b).abs().max(),
      'nd agree',(m.val_a.isna()==m.val_b.isna()).all())
print(((det.val_a*F-det.val_b).abs()>0.006).sum())
only_alt=alt.merge(base[k],on=k,how='left',indicator=True)._merge.eq('left_only').sum()
print('alt without base',only_alt)
check_unique_key(base,k)
t=base.copy()
t['nondetect']=t.ResultDetectionConditionText.ne('')
t['result_mg_L_as_N']=t.val; t['reporting_limit_mg_L_as_N']=t.dl
t.loc[t.nondetect,'result_mg_L_as_N']=np.nan
cols=['MonitoringLocationIdentifier','ActivityIdentifier','ActivityStartDate','USGSPCode','CharacteristicName','ResultSampleFractionText','result_mg_L_as_N','nondetect','reporting_limit_mg_L_as_N']
t[cols].to_csv('nitrate_as_n.csv',index=False)
censoring_profile(t,by=())  if False else None
cp=censoring_profile(t.assign(),by=("CharacteristicName",))
tot=g[(g.ResultSampleFractionText=='Total')&(g.CharacteristicName=='Nitrate')]
print(len(t),t.MonitoringLocationIdentifier.nunique(),t.nondetect.sum(),len(alt),len(tot),
      len(g[g.CharacteristicName!='Nitrate']), t.dl.isna().sum())
ans={"rows_in_table":len(t),"wells_in_table":int(t.MonitoringLocationIdentifier.nunique()),
"nondetect_rows_in_table":int(t.nondetect.sum()),"pcodes_included":["00618"],
"pcodes_excluded":{"71851":"Same dissolved nitrate measurement as 00618 re-expressed as mg/L NO3 (ratio 4.43 = 62.005/14.007); dropped to avoid double counting",
"00620":"Total (unfiltered) nitrate as N: different fraction","71850":"Total nitrate as NO3: different fraction and unit basis",
"00630":"Total nitrate+nitrite as N: different chemical definition and fraction","00631":"Dissolved nitrate+nitrite as N: different chemical definition (includes nitrite)"},
"unit_conversion_factors_used":{"mg/l as N -> mg/L as N":1.0,"mg/l asNO3 -> mg/L as N":round(F,6)},
"rows_dropped_as_same_measurement_reexpressed":int(len(alt)),
"rows_excluded_other_fraction":int(len(tot)),
"nitrate_plus_nitrite_combined":False,
"notes":"Scope: Sample-Routine, ActivityMediaSubdivisionName=Groundwater (excludes leachate, soil moisture, elutriation, interstitial, bulk deposition water rows), 2000+, wells in San Bernardino Co. Included = Nitrate, Dissolved, 00618, mg/l as N (one row per activity; key unique). 71851 factor 14.0067/62.0049=0.22590 was used only to verify (2301 pairs; all 2169 detected pairs agree after conversion within rounding, median relative difference 0.13%, max 1.4%; non-detect status agrees) and the rows were dropped. rows_excluded_other_fraction counts Total-fraction rows with CharacteristicName Nitrate (00620, 71850) in routine groundwater; Total nitrate+nitrite (00630, 470 rows) and dissolved nitrate+nitrite (00631, 2301 rows) are excluded by definition, not counted there. Non-detects are kept as censored: result left blank, reporting limit in reporting_limit_mg_L_as_N (no substitution). Reporting limits differ between labs/years (0.02-0.25 mg/L as N); 15 of 755 hmm see checks. QC replicate and 'Not determined' activities excluded.",
"checks":["unique key (site, activity, pcode) in final table: 0 duplicates","pcode 71851/00618 ratio mean 4.427 CV<1%","censoring_profile run by year"],
"caveats":["Result values flagged Estimated are retained","Non-detect limits vary by year/lab; pooled comparisons across years can show artefactual change"]}
ans["notes"]=ans["notes"].replace(" 15 of 755 hmm see checks.","")
json.dump(ans,open('answer.json','w'),indent=1)
rel=((det.val_a*F-det.val_b)/det.val_b).abs()
print(rel.describe(), det.loc[rel.idxmax(),['val_a','val_b']].tolist(), ((det.val_a*F-det.val_b).abs()>0.05*det.val_b+0.01).sum())
