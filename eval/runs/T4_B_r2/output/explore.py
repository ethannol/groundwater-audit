import sys; sys.path.insert(0,"/Users/ethannol/.cache/gwaudit/gwaudit_T4_B_r2_ufc5eqlh/work")
import pandas as pd
import validators as v
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
n=d[d.CharacteristicName.isin(['Nitrate','Inorganic nitrogen (nitrate and nitrite)'])]
for c in ['ActivityTypeCode','ActivityMediaName','ActivityMediaSubdivisionName','CharacteristicName','USGSPCode','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','MethodSpeciationName','ResultDetectionConditionText','MeasureQualifierCode','ResultStatusIdentifier','DetectionQuantitationLimitTypeName','DetectionQuantitationLimitMeasure/MeasureUnitCode','ResultValueTypeName']:
    print(n[c].value_counts(dropna=False).head(15),'\n')
print(n.groupby(['CharacteristicName','USGSPCode','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','MethodSpeciationName'],dropna=False).size())
