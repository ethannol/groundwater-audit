import pandas as pd
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
n=df[df.USGSPCode=="00618"]
for c in ["ActivityTypeCode","ActivityMediaSubdivisionName","ResultDetectionConditionText","ResultValueTypeName","MeasureQualifierCode","DetectionQuantitationLimitMeasure/MeasureUnitCode","ResultMeasure/MeasureUnitCode","DetectionQuantitationLimitTypeName"]:
    print(n[c].value_counts().to_dict())
print(n[n.ResultDetectionConditionText!=""][["ActivityStartDate","ResultMeasureValue","DetectionQuantitationLimitMeasure/MeasureValue","LaboratoryName"]].assign(y=lambda d:d.ActivityStartDate.str[:4]).groupby(["y","DetectionQuantitationLimitMeasure/MeasureValue"]).size())
print(n[(n.ResultDetectionConditionText=="")&(n.ResultMeasureValue=="")].shape)
print(n.groupby(["MonitoringLocationIdentifier","ActivityStartDate","ActivityTypeCode"]).size().value_counts())
