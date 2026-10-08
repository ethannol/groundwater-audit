import pandas as pd
from validators import *
df=pd.read_csv("data/wqp_result.csv",dtype=str,keep_default_na=False)
print(df.columns.tolist())
a=df[df.CharacteristicName=="Arsenic"]
tabulate_fields(a,top=20)
print(a.groupby(["USGSPCode","ResultSampleFractionText","ResultMeasure/MeasureUnitCode"]).size())
