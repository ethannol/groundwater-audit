import pandas as pd
r=pd.read_csv('data/wqp_result.csv',low_memory=False,dtype={'USGSPCode':str})
n=r[r.USGSPCode=='00618']
print(len(n))
for c in ['ActivityTypeCode','ActivityMediaSubdivisionName','CharacteristicName','ResultSampleFractionText','ResultMeasure/MeasureUnitCode','MeasureQualifierCode','ResultStatusIdentifier','ResultDetectionConditionText','DetectionQuantitationLimitTypeName','ResultValueTypeName','StatisticalBaseCode']:
    print(n[c].value_counts(dropna=False).head(12),'\n')
print(n['ResultMeasureValue'].isna().sum())
print(n[n.ResultMeasureValue.isna()][['ResultDetectionConditionText','DetectionQuantitationLimitMeasure/MeasureValue','ResultMeasure/MeasureUnitCode']].value_counts(dropna=False).head())
print(n.ActivityStartDate.min(),n.ActivityStartDate.max())
print(n.duplicated(['MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time','ResultMeasureValue']).sum())
