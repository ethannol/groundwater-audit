import sys; sys.path.insert(0,".")
import pandas as pd, numpy as np
from validators import *
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
n=d[d.CharacteristicName.isin(['Nitrate','Inorganic nitrogen (nitrate and nitrite)'])]
g=n[(n.ActivityTypeCode=='Sample-Routine')&(n.ActivityMediaSubdivisionName=='Groundwater')]
print(len(n),len(g))
print(g.groupby(['CharacteristicName','USGSPCode','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','ResultDetectionConditionText']).size())
print(g.groupby(['USGSPCode','DetectionQuantitationLimitMeasure/MeasureUnitCode']).size())
nd=g[g.ResultDetectionConditionText!='']
print(nd[['ResultMeasureValue','DetectionQuantitationLimitMeasure/MeasureValue']].replace('',np.nan).notna().sum())
print(g[g.ResultMeasureValue==''].ResultDetectionConditionText.value_counts())
print(g.ResultValueTypeName.value_counts())
print(g.ActivityStartTime_Time if False else '')
c=g[g.USGSPCode.isin(['00618','71851'])]
check_unique_key(c,['MonitoringLocationIdentifier','ActivityIdentifier','USGSPCode'])
check_reexpressed_pairs(c,['MonitoringLocationIdentifier','ActivityIdentifier'])
a=c.groupby('ActivityIdentifier').USGSPCode.agg(lambda s:tuple(sorted(set(s))))
print(a.value_counts())
c=c.copy()
c['v']=pd.to_numeric(c.ResultMeasureValue.replace('',np.nan))
p=c.pivot_table(index=['MonitoringLocationIdentifier','ActivityIdentifier'],columns='USGSPCode',values='v',aggfunc='first')
print(p.dropna().assign(r=lambda x:x['71851']/x['00618']).r.describe())
# nondetect pairing & dl
for k in ['00618','71851']:
    x=c[(c.USGSPCode==k)&(c.ResultDetectionConditionText!='')]
    print(k,x['DetectionQuantitationLimitMeasure/MeasureValue'].astype(float).describe())
print(c.groupby('ActivityIdentifier').USGSPCode.agg(lambda s:tuple(sorted(s))).value_counts())
print(c.groupby(['MonitoringLocationIdentifier','ActivityIdentifier','USGSPCode']).size().max())
print(c.groupby(['MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time']).ActivityIdentifier.nunique().value_counts())
