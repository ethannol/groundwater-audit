import sys; sys.path.insert(0,'.')
import pandas as pd
from validators import *
pd.set_option('display.width',250,'display.max_rows',500,'display.max_columns',50)
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
tabulate_fields(d)
for c in ['ResultLaboratoryCommentText','ResultCommentText','DetectionQuantitationLimitTypeName','ResultAnalyticalMethod/MethodName']: print(d[c].value_counts())
check_unique_key(d,['ActivityIdentifier','USGSPCode']);check_unique_key(d,['ResultIdentifier'])
print(d[['MonitoringLocationIdentifier','ActivityStartDate','ActivityTypeCode','CharacteristicName','ResultSampleFractionText','ResultMeasureValue','ResultMeasure/MeasureUnitCode','ResultDetectionConditionText','DetectionQuantitationLimitMeasure/MeasureValue','DetectionQuantitationLimitMeasure/MeasureUnitCode','USGSPCode','LaboratoryName']].to_string())
