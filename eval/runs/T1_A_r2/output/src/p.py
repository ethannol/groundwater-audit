import pandas as pd
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
d=d.replace('',pd.NA)
print(len(d))
for c in ['ActivityMediaName','ActivityMediaSubdivisionName','ActivityTypeCode','CharacteristicName','ResultSampleFractionText','ResultDetectionConditionText','ResultMeasure/MeasureUnitCode','DetectionQuantitationLimitTypeName','DetectionQuantitationLimitMeasure/MeasureUnitCode','ResultStatusIdentifier','MeasureQualifierCode']:
    print(d[c].value_counts(dropna=False).to_string(),'\n')
print(pd.crosstab(d.ActivityMediaName.fillna('NA'),d.ActivityMediaSubdivisionName.fillna('NA')))
gw=d[(d.ActivityMediaName=='Water')&(d.ActivityMediaSubdivisionName=='Groundwater')]
print(gw.ActivityTypeCode.value_counts(dropna=False))
print(d.isna().mean().round(3).to_string())
