import pandas as pd
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
a=d[d.USGSPCode.astype(str).str.zfill(5)=='01000']
print(len(a))
for c in ['ActivityTypeCode','ActivityMediaSubdivisionName','CharacteristicName','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','MeasureQualifierCode','ResultStatusIdentifier','ResultDetectionConditionText','DetectionQuantitationLimitTypeName','DetectionQuantitationLimitMeasure/MeasureUnitCode','ResultValueTypeName']:
    print(a[c].value_counts(dropna=False).head(12))
print(a[a.ResultMeasureValue.isna()][['ResultDetectionConditionText','DetectionQuantitationLimitMeasure/MeasureValue','MeasureQualifierCode']].value_counts(dropna=False).head(20))
print(a.duplicated(['MonitoringLocationIdentifier','ActivityStartDate','ActivityIdentifier']).sum())
print(a.ResultMeasureValue.describe())
