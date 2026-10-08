import pandas as pd
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
print(d.columns.tolist())
for c in ['ActivityMediaName','ActivityMediaSubdivisionName','ActivityTypeCode','CharacteristicName','ResultSampleFractionText','ResultDetectionConditionText','ResultMeasure/MeasureUnitCode','USGSPCode','MethodSpeciationName','ResultStatusIdentifier','DetectionQuantitationLimitTypeName','DetectionQuantitationLimitMeasure/MeasureUnitCode','MeasureQualifierCode']:
    print(d[c].value_counts(dropna=False).head(15),'\n')
print(d.isna().mean().sort_values().to_string())
