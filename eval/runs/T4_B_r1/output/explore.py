import pandas as pd
from validators import *
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
n=df[df.CharacteristicName.isin(["Nitrate","Inorganic nitrogen (nitrate and nitrite)"])]
tabulate_fields(n)
print(n.groupby(["CharacteristicName","USGSPCode","ResultSampleFractionText","ResultMeasure/MeasureUnitCode","MethodSpeciationName"]).size())
print(n.ResultIdentifier.duplicated().sum())
