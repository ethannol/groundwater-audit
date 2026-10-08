import sys; sys.path.insert(0,".")
import pandas as pd, numpy as np
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
a=df[(df.USGSPCode=="01000")&(df.ActivityTypeCode=="Sample-Routine")&(df.ActivityMediaSubdivisionName=="Groundwater")]
d=a[a.duplicated(["MonitoringLocationIdentifier","ActivityStartDate"],keep=False)].sort_values(["MonitoringLocationIdentifier","ActivityStartDate"])
pd.set_option("display.width",250)
print(d[["MonitoringLocationIdentifier","ActivityStartDate","ActivityStartTime/Time","ActivityIdentifier","ResultMeasureValue","ResultDetectionConditionText","ResultAnalyticalMethod/MethodIdentifier","ResultStatusIdentifier","ResultSampleFractionText","ProjectIdentifier"]].head(24).to_string())
print(d.groupby(["MonitoringLocationIdentifier","ActivityStartDate"]).ActivityIdentifier.nunique().value_counts())
print(d.groupby(["MonitoringLocationIdentifier","ActivityStartDate"]).ResultMeasureValue.nunique().value_counts())
