import pandas as pd
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
d['y']=d.ActivityStartDate.str[:4]
print(d.y.value_counts())
print(d.groupby(['y','LaboratoryName','ResultMeasure/MeasureUnitCode','ResultDetectionConditionText','DetectionQuantitationLimitMeasure/MeasureValue']).size())
print(d.groupby('MonitoringLocationIdentifier').y.apply(lambda x:''.join(sorted(v[2:] for v in x))).value_counts())
print(d[d.LaboratoryName.str.contains('B')][['MonitoringLocationIdentifier','y','ResultMeasureValue','ResultMeasure/MeasureUnitCode']])
s=pd.read_csv('data/wqp_station.csv',dtype=str,keep_default_na=False)
print(s.iloc[:,1:].drop_duplicates(subset=s.columns[2:]).to_string()); print(set(d.MonitoringLocationIdentifier)-set(s.MonitoringLocationIdentifier), len(set(s.MonitoringLocationIdentifier)))
print(d.groupby('MonitoringLocationIdentifier').size().value_counts())
print(d[d.y=='2005'].ResultMeasureValue.describe(), d[d.ResultMeasureValue!=''].groupby('y').ResultMeasureValue.apply(lambda x:sorted(map(float,x))))
