import pandas as pd
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
d=d[d.CharacteristicName!='Arsenic']
pd.set_option('display.width',250,'display.max_rows',500)
c=['ActivityTypeCode','ActivityMediaName','ActivityMediaSubdivisionName','CharacteristicName','ResultSampleFractionText','USGSPCode','ResultMeasure/MeasureUnitCode']
print(d.groupby(c,dropna=False).size())
print(d.ResultDetectionConditionText.value_counts(dropna=False))
print(d.MeasureQualifierCode.value_counts(dropna=False).head(15))
print(d.ResultStatusIdentifier.value_counts(dropna=False))
print(d.ResultValueTypeName.value_counts(dropna=False))
print(d['ResultAnalyticalMethod/MethodName'].groupby(d.USGSPCode).value_counts())
