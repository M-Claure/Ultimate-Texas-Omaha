import sys,glob; sys.path.insert(0,'src')
import numpy as np, pandas as pd
from uto.player_split import book_split
from uto.features import split_features
fs=sorted(glob.glob('experiments/EXP-004/chunks/hands_*.npz'))
d=[np.load(f) for f in fs]; H=np.concatenate([x['hands'] for x in d]).astype(np.int64); SV=np.concatenate([x['sv'] for x in d])
rows=[]
for h,sv in zip(H,SV):
    p=book_split(h); f=split_features(h,p); f['vR']=sv[p,1]; f['vC']=sv[p,2]; rows.append(f)
df=pd.DataFrame(rows); df.to_pickle('experiments/EXP-005/_pre_b2.pkl')
opt=np.maximum(df.vR,df.vC).mean()
P=lambda d:(d.he_pair==1); AK=lambda d:(d.he_pair==0)&(d.he_hi==12)&(d.he_lo==11)
R2=lambda d:(P(d)&((d.he_hi>=9)|((d.he_hi==8)&(d.om_high>=2))|((d.he_hi==7)&(d.om_high>=3))))|(AK(d)&(d.om_high>=2))
print("optimal",round(opt,4),"R2 cost",round((opt-np.where(R2(df),df.vR,df.vC).mean())*100,3))
# search: pair thresholds by om_high
best=None
for jj in [0,1]:          # JJ needs om_high >= jj
  for tt in [1,2,3]:
    for nn in [2,3,4]:
      for ak in [1,2,3,9]:
        for aq in [3,9]:
          f=lambda d:(P(d)&((d.he_hi>=10)|((d.he_hi==9)&(d.om_high>=jj))|((d.he_hi==8)&(d.om_high>=tt))|((d.he_hi==7)&(d.om_high>=nn))))|(AK(d)&(d.om_high>=ak))|((d.he_pair==0)&(d.he_hi==12)&(d.he_lo==10)&(d.om_high>=aq))
          v=np.where(f(df),df.vR,df.vC).mean()
          if best is None or v>best[0]: best=(v,jj,tt,nn,ak,aq)
print("best grid",best, "cost",round((opt-best[0])*100,3))
