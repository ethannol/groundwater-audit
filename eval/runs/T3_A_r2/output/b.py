import pandas as pd
d=pd.read_csv('data/wqp_result.csv',low_memory=False,dtype={'USGSPCode':str})
d=d[(d.USGSPCode=='01000')&(d.ActivityTypeCode=='Sample-Routine')&(d.ActivityMediaSubdivisionName=='Groundwater')].copy()
d['y']=pd.to_datetime(d.ActivityStartDate).dt.year
d['v']=d['ResultMeasureValue'];d['dl']=d['DetectionQuantitationLimitMeasure/MeasureValue']
d['nd']=d.ResultDetectionConditionText.eq('Not Detected')
print(d.groupby('y').agg(n=('v','size'),nd=('nd','sum'),vmiss=('v',lambda s:s.isna().sum()),dlmin=('dl','min'),dlmax=('dl','max')))
print(d[d.ResultDetectionConditionText.notna()][['ResultDetectionConditionText','v','dl']].describe(include='all'))
print(d[d.ResultDetectionConditionText=='Detected Not Quantified'][['y','v','dl']])
print(d[~d.nd&(d.v<=d.dl)][['y','v','dl']].head(), (d.v<d.dl).sum())
print(d[d.nd].groupby(pd.cut(d.y,[1999,2011,2023,2100])).dl.describe())
print(d[~d.nd].groupby(pd.cut(d.y,[1999,2011,2023,2100])).v.describe())
