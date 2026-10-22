import sys,glob; sys.path.insert(0,'src')
import numpy as np, pandas as pd
from uto.player_split import _PIDX
def sp(i,j): return _PIDX[tuple(sorted([i,j]))]
fs=sorted(glob.glob('experiments/EXP-004/chunks/hands_*.npz'))
d=[np.load(f) for f in fs]; H=np.concatenate([x['hands'] for x in d]).astype(np.int64); V=np.concatenate([x['sv'] for x in d])[:,:,0]
rows=[]
for h,v in zip(H,V):
    r=h>>2; c=np.bincount(r,minlength=13)
    if sorted(c[c>0].tolist())!=[1,1,2,2]: continue
    ps=sorted([x for x in range(13) if c[x]==2],reverse=True); hp=[k for k in range(6) if r[k]==ps[0]]; lp=[k for k in range(6) if r[k]==ps[1]]
    si=sorted([k for k in range(6) if c[r[k]]==1],key=lambda k:-r[k])
    rows.append(dict(hi=ps[0],lo=ps[1],s1=r[si[0]],high=v[sp(*hp)],low=v[sp(*lp)],singles=v[sp(*si)]))
df=pd.DataFrame(rows)
print(len(df), df[['high','low','singles']].mean().round(4).to_dict())
print(df.assign(lo_better=df.low>df.high).groupby('hi').agg(high=('high','mean'),low=('low','mean'),singles=('singles','mean'),n=('high','size')).round(3))
print(df.groupby('s1').agg(high=('high','mean'),singles=('singles','mean'),n=('high','size')).round(3))
