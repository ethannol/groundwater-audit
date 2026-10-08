import pandas as pd
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
for c in ['ActivityTypeCode','ActivityMediaName','ActivityMediaSubdivisionName','CharacteristicName','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','ResultDetectionConditionText','USGSPCode','DetectionQuantitationLimitTypeName','DetectionQuantitationLimitMeasure/MeasureUnitCode','MeasureQualifierCode','ResultStatusIdentifier','MethodSpeciationName']:
    print(d[c].value_counts(dropna=False).head(15),'\n')
print((d.isna().mean()).round(3).to_string())
