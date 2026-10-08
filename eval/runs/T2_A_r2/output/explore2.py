import pandas as pd
d=pd.read_csv('data/wqp_result.csv',low_memory=False)
g=d[(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaName=='Water')&(d.ActivityMediaSubdivisionName=='Groundwater')&(d.CharacteristicName=='Nitrate')].copy()
k=['OrganizationIdentifier','ActivityIdentifier']
print(len(g), g.groupby('USGSPCode').size())
p=g.groupby(k).USGSPCode.apply(lambda s:tuple(sorted(s)));print(p.value_counts())
a=g[g.USGSPCode==618]; print(a.duplicated(k).sum())
print(a[a['ResultMeasure/MeasureUnitCode'].isna()][['ResultMeasureValue','ResultDetectionConditionText','DetectionQuantitationLimitMeasure/MeasureValue','DetectionQuantitationLimitMeasure/MeasureUnitCode']].describe(include='all'))
print(a.ResultDetectionConditionText.value_counts(dropna=False), a.ResultMeasureValue.isna().sum())
b=g[g.USGSPCode==71851].merge(a,on=k)
b=b.assign(r=b.ResultMeasureValue_x/b.ResultMeasureValue_y); print(b.r.describe())
print(g[g.USGSPCode==71851].ResultMeasureValue.isna().sum())
print(a[['ResultMeasureValue','DetectionQuantitationLimitMeasure/MeasureValue']].head(0))
nd=a[a.ResultDetectionConditionText.notna()];print(nd[['ResultMeasureValue','DetectionQuantitationLimitMeasure/MeasureValue','DetectionQuantitationLimitMeasure/MeasureUnitCode']].describe(include='all'))
