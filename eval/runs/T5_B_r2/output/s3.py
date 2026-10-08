import pandas as pd
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
a=df[(df.USGSPCode=="01000")&(df.ActivityTypeCode=="Sample-Routine")&(df.ActivityMediaSubdivisionName=="Groundwater")]
print(a[a.ResultDetectionConditionText=="Detected Not Quantified"][["MonitoringLocationIdentifier","ActivityStartDate","ResultMeasureValue","DetectionQuantitationLimitMeasure/MeasureValue","DetectionQuantitationLimitTypeName"]])
nd=a[a.ResultDetectionConditionText=="Not Detected"]
print(nd.DetectionQuantitationLimitTypeName.value_counts(), (nd.ResultMeasureValue!="").sum(), (nd["DetectionQuantitationLimitMeasure/MeasureValue"]=="").sum())
d=a[a.ResultDetectionConditionText==""]
print((d.ResultMeasureValue=="").sum(), (d["ResultMeasure/MeasureUnitCode"]!="ug/l").sum())
print(pd.to_numeric(d.ResultMeasureValue).describe())
print(a.groupby(a.ActivityStartDate.str[:10]).size().max())
