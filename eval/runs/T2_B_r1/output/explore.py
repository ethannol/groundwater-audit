import pandas as pd
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
n=d[d.CharacteristicName.isin(['Nitrate','Inorganic nitrogen (nitrate and nitrite)'])]
for c in ['ActivityTypeCode','ActivityMediaName','ActivityMediaSubdivisionName','ResultDetectionConditionText','MethodSpeciationName','ResultStatusIdentifier','MeasureQualifierCode','DetectionQuantitationLimitTypeName']:
    print(n[c].value_counts(dropna=False).head(10))
print(n.groupby(['CharacteristicName','USGSPCode','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','MethodSpeciationName'],dropna=False).size())
