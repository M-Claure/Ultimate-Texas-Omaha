import sys,glob,itertools; sys.path.insert(0,'src')
import numpy as np, pandas as pd
exec(open('experiments/EXP-005/np_tree2.py').read().split("fs=sorted")[0])
fs=sorted(glob.glob('experiments/EXP-004/chunks/hands_*.npz'))
H,V=load(fs[2:])
rows=[]
for h,v in zip(H,V):
    if len(set(h>>2))<6: continue
    m,f=menu_feats(h); f.update({k:v[m[k]] for k in OPTS}); rows.append(f)
df=pd.DataFrame(rows)
o2=np.load('experiments/EXP-004/split_oos.npz'); H2=o2['hands']; S2=o2['sv2']
rows2=[]
for i,h in enumerate(H2):
    if len(set(h>>2))<6: continue
    m,f=menu_feats(h); f.update({k:S2[i,m[k]] for k in OPTS}); rows2.append(f)
dv=pd.DataFrame(rows2)
def rule(d, c1, acecut, lowcond):
    # returns chosen value
    v=np.where(d.second>=c1, d.top2,
      np.where(d.top>=acecut, d.ace_lowsuit,
        np.where(lowcond(d), d.low2, d.top2)))
    return v.mean()
conds={"always low2":lambda d:np.ones(len(d),bool),"nQ<=0":lambda d:d.nQ==0,"nhigh<=1":lambda d:d.nhigh<=1,"nhigh<=2":lambda d:d.nhigh<=2,
       "low2 suited or nhigh<=1":lambda d:(d.low2_suited==1)|(d.nhigh<=1)}
res=[]
for c1 in [9,10,11,12,13]:
    for ac in [11,12,13]:
        for cn,cf in conds.items():
            res.append((rule(df,c1,ac,cf),rule(dv,c1,ac,cf),c1,ac,cn))
res.sort(reverse=True)
for r in res[:12]: print(f"train {r[0]:.4f} OOS {r[1]:.4f}  second>={r[2]} acecut>={r[3]} low2 if {r[4]}")
print("baseline top2 train",round(df.top2.mean(),4),"OOS",round(dv.top2.mean(),4))
def r2(d):
    return np.where(d.second>=10,d.top2,np.where(d.low2_suited==1,d.low2,np.where(d.top>=11,d.ace_lowsuit,d.low2))).mean()
print("variant low2-suited first: train",round(r2(df),4),"OOS",round(r2(dv),4))
