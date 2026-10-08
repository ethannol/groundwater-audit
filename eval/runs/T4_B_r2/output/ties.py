exec(open('analysis.py').read().split("# last result")[0].replace("v.censoring_profile","(lambda *a,**k:None)").replace("print(","(lambda *a,**k:None)("))
import itertools
r=r.sort_values(['MonitoringLocationIdentifier','date','ActivityStartTime/Time'])
g=r.groupby(['MonitoringLocationIdentifier','period'])
t=r[r.date==g.date.transform('max')]
t=t[t.duplicated(['MonitoringLocationIdentifier','period'],keep=False)]
print(len(t),t.MonitoringLocationIdentifier.nunique())
print(t[['MonitoringLocationIdentifier','ActivityStartDate','ActivityStartTime/Time','ActivityIdentifier','val','dl','nd','ProjectName']].head(16).to_string())
cols=['MonitoringLocationIdentifier','period']
last=r.groupby(cols).tail(1)
w=last.pivot(index='MonitoringLocationIdentifier',columns='period',values=['lo','hi']).dropna()
coh=set(w.index)
tt=t[t.MonitoringLocationIdentifier.isin(coh)]
print('cohort wells with ties',tt.MonitoringLocationIdentifier.nunique())
def run(sel):
    L=sel.groupby(cols)
    x=L.agg(lo=('lo','first'),hi=('hi','first')).unstack().dropna()
    el,eh,ll,lh=x[('lo','early')],x[('hi','early')],x[('lo','late')],x[('hi','late')]
    return len(x),int((lh<el).sum()),int((ll>eh).sum()),int(len(x)-(lh<el).sum()-(ll>eh).sum()),el.median(),ll.median()
# same-date: aggregate by day-mean as sensitivity, plus max/min choice
for name,f in [('last row',lambda s:s.groupby(cols).tail(1)),
  ('day-min',lambda s:s[s.date==s.groupby(cols).date.transform('max')].sort_values('hi').groupby(cols).head(1)),
  ('day-max',lambda s:s[s.date==s.groupby(cols).date.transform('max')].sort_values('hi').groupby(cols).tail(1))]:
    print(name,run(f(r)))
