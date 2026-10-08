import pandas as pd
from validators import *
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
tabulate_fields(df,top=30)
n=df[df.CharacteristicName!="Arsenic"]
print(n.groupby(["ActivityTypeCode","ActivityMediaName","ActivityMediaSubdivisionName"]).size())
print(n.groupby(["CharacteristicName","USGSPCode","ResultSampleFractionText","ResultMeasure/MeasureUnitCode","MethodSpeciationName"]).size())
print(n.groupby(["USGSPCode","ResultDetectionConditionText","DetectionQuantitationLimitMeasure/MeasureUnitCode"]).size())
