import pandas as pd
d=pd.read_csv('data/wqp_result.csv',dtype={'USGSPCode':str},low_memory=False)
a=d[d.USGSPCode=='01000'].copy()
print(len(d),len(a))
for c in ['CharacteristicName','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','ActivityTypeCode','ActivityMediaName','ActivityMediaSubdivisionName','ResultDetectionConditionText','MeasureQualifierCode','ResultStatusIdentifier','DetectionQuantitationLimitTypeName','DetectionQuantitationLimitMeasure/MeasureUnitCode','MethodSpeciationName','ResultValueTypeName','LaboratoryName','ResultAnalyticalMethod/MethodIdentifier']:
    print(a[c].value_counts(dropna=False).head(15),'\n')
a['yr']=a.ActivityStartDate.str[:4].astype(int)
print(a.groupby('yr').agg(n=('yr','size'),nd=('ResultDetectionConditionText',lambda s:s.notna().sum()),dl=('DetectionQuantitationLimitMeasure/MeasureValue',lambda s:s.notna().sum()),mv=('ResultMeasureValue',lambda s:s.notna().sum())))
print(a.ResultIdentifier.is_unique)
