import pandas as pd
s=pd.read_csv('data/wqp_station.csv',dtype=str,keep_default_na=False)
print(((s=='').mean()).round(2)[lambda x:x>0.05].to_string())
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
a=d[(d.ActivityMediaSubdivisionName=='Groundwater')&(d.ActivityTypeCode=='Sample-Routine')&(d.CharacteristicName=='Arsenic')&(d.ResultSampleFractionText=='Dissolved')]
print((a=='').mean().round(2)[lambda x:x>0.05].to_string())
print(a.MonitoringLocationIdentifier.isin(s.MonitoringLocationIdentifier).mean())
