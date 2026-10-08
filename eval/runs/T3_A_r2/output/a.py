import pandas as pd
d=pd.read_csv('data/wqp_result.csv',low_memory=False,dtype={'USGSPCode':str})
d=d[(d.USGSPCode=='01000')]
print(len(d))
for c in ['CharacteristicName','ResultSampleFractionText','ActivityTypeCode','ActivityMediaSubdivisionName','ResultMeasure/MeasureUnitCode','MeasureQualifierCode','ResultDetectionConditionText','DetectionQuantitationLimitTypeName','DetectionQuantitationLimitMeasure/MeasureUnitCode','ResultStatusIdentifier','ResultValueTypeName']:
    print(d[c].value_counts(dropna=False).head(15))
