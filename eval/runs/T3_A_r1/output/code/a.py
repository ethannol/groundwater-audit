import pandas as pd
d=pd.read_csv('data/wqp_result.csv',dtype=str)
d=d[(d.USGSPCode=='01000')]
for c in ['CharacteristicName','ResultSampleFractionText','ActivityTypeCode','ResultMeasure/MeasureUnitCode','ResultDetectionConditionText','MeasureQualifierCode','ResultStatusIdentifier','DetectionQuantitationLimitTypeName','DetectionQuantitationLimitMeasure/MeasureUnitCode','ActivityMediaSubdivisionName']:
    print(d[c].value_counts(dropna=False).head(15),'\n')
d['y']=d.ActivityStartDate.str[:4].astype(int)
print(d.y.value_counts().sort_index())
nd=d[d['ResultMeasureValue'].isna()|d.MeasureQualifierCode.notna()]
print(nd[['y','ResultMeasureValue','MeasureQualifierCode','ResultDetectionConditionText','DetectionQuantitationLimitMeasure/MeasureValue']].value_counts(dropna=False).head(40))
