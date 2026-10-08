import sys; sys.path.insert(0,".")
import pandas as pd
from validators import *
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
a=df[df.CharacteristicName=="Arsenic"]
print(len(a))
tabulate_fields(a,top=20)
print(a.groupby(["USGSPCode","ResultSampleFractionText","ResultMeasure/MeasureUnitCode","MethodSpeciationName","ActivityTypeCode"]).size())
print(a["ResultDetectionConditionText"].value_counts(), a["MeasureQualifierCode"].value_counts())
print(a.ResultStatusIdentifier.value_counts())
