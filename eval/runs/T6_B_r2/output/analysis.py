import pandas as pd, numpy as np, json
from validators import *
d=pd.read_csv('data/wqp_result.csv',dtype=str,keep_default_na=False)
d['y']=d.ActivityStartDate.str[:4]
d['v']=pd.to_numeric(d.ResultMeasureValue.replace('',np.nan))
d['nd']=d.ResultDetectionConditionText!=''
d['dl']=pd.to_numeric(d['DetectionQuantitationLimitMeasure/MeasureValue'])
d['labB']=d.LaboratoryName.str.contains('Lab B')
checks=[check_unique_key(d,['MonitoringLocationIdentifier','ActivityStartDate']),
        check_unique_key(d,['ResultIdentifier']), cohort_composition(d,'MonitoringLocationIdentifier','y')]
censoring_profile(d,by=('LaboratoryName',))
e=d[d.y=='2005'].set_index('MonitoringLocationIdentifier'); l=d[d.y=='2018'].set_index('MonitoringLocationIdentifier')
c=e.index.intersection(l.index)
dirs=[]
for w in c:
    lo_e,hi_e=(0,e.dl[w]) if e.nd[w] else (e.v[w],e.v[w])
    lo_l,hi_l=(0,l.dl[w]) if l.nd[w] else (l.v[w],l.v[w])
    dirs.append('decline' if hi_l<lo_e else 'increase' if lo_l>hi_e else 'indet')
s=pd.Series(dirs,index=c); print(s.value_counts())
print(pd.crosstab(s,l.labB[c]))
# exclude Lab B sensitivity
cA=[w for w in c if not l.labB[w]]; print('LabA-only dirs',s[cA].value_counts().to_dict())
# detected-only early wells
det=[w for w in c if not e.nd[w]]
print('early detected wells',len(det),e.v[det].round(2).tolist(),l.v[det].round(2).tolist())
# pooled medians: ND at limit (labelled substitution), and bounds
def med(x,mode):
    v=np.where(x.nd,{'lo':0,'hi':x.dl}[mode],x.v); return float(np.median(v))
for nm,x in [('early',e),('late',l),('late_cohort',l.loc[c])]:
    print(nm,len(x),med(x,'lo'),med(x,'hi'))
print('late nonLabB cohort+N', med(l[~l.labB],'lo'))
print('early detect frac',(~e.nd).mean(),'late values>=2:',(l.v>=2).sum())
# exact sign test on determinate directions
from scipy.stats import binomtest
print(s.value_counts().to_dict())
json.dump({'dirs':s.value_counts().to_dict()},open('/tmp/x.json','w'))
