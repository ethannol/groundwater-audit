import pandas as pd
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
a=df[(df.USGSPCode=="01000")]
print(pd.crosstab(a.ActivityTypeCode,a.ActivityMediaSubdivisionName))
r=a[a.ActivityTypeCode=="Sample-Routine"]
print(pd.crosstab(r.ActivityMediaSubdivisionName,r.ResultDetectionConditionText))
print(r.ResultStatusIdentifier.value_counts(), r.ActivityStartDate.str[:4].value_counts().sort_index().to_dict())
c=r[r.ResultDetectionConditionText!=""]
print(c.groupby([c.ActivityStartDate.str[:4],"DetectionQuantitationLimitMeasure/MeasureValue"]).size().to_string())
print(r[(r.ResultMeasureValue=="")&(r.ResultDetectionConditionText=="")].shape)
print(r[r.ResultMeasureValue!=""].groupby("DetectionQuantitationLimitMeasure/MeasureValue").size().head(20))
print(r.duplicated(["MonitoringLocationIdentifier","ActivityStartDate","ActivityStartTime/Time"],keep=False).sum(), r.ResultIdentifier.duplicated().sum())
print(r.MeasureQualifierCode.value_counts())
