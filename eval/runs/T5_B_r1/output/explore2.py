import sys; sys.path.insert(0,".")
import pandas as pd
from validators import *
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
a=df[(df.USGSPCode=="01000")]
print(pd.crosstab(a.ActivityTypeCode,a.ActivityMediaSubdivisionName))
r=a[(a.ActivityTypeCode=="Sample-Routine")]
print(pd.crosstab(r.ActivityMediaSubdivisionName,r.ResultDetectionConditionText))
r=r[r.ActivityMediaSubdivisionName=="Groundwater"].copy()
r["yr"]=r.ActivityStartDate.str[:4].astype(int)
c=r[r.ResultDetectionConditionText!=""]
print(c[["ResultMeasureValue","ResultMeasure/MeasureUnitCode","DetectionQuantitationLimitMeasure/MeasureValue","DetectionQuantitationLimitMeasure/MeasureUnitCode","DetectionQuantitationLimitTypeName"]].drop_duplicates().head(30))
print(c.groupby(["yr","DetectionQuantitationLimitMeasure/MeasureValue"]).size().to_string())
d=r[r.ResultDetectionConditionText==""]
print((d.ResultMeasureValue=="").sum(), d.ResultValueTypeName.value_counts(), d["DetectionQuantitationLimitMeasure/MeasureValue"].ne("").sum())
print(d.ResultMeasureValue.astype(float).describe())
print(r.duplicated(["MonitoringLocationIdentifier","ActivityStartDate","ActivityStartTime/Time"],keep=False).sum())
print(r.ActivityStartDate.str.len().value_counts(), r.yr.value_counts().sort_index().to_string())
