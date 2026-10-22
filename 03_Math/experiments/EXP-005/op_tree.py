import sys,glob; sys.path.insert(0,'src')
import numpy as np, pandas as pd
from uto.player_split import _PIDX
def sp(i,j): return _PIDX[tuple(sorted([i,j]))]
def load(chunks):
    d=[np.load(f) for f in chunks]; return np.concatenate([x['hands'] for x in d]).astype(np.int64), np.concatenate([x['sv'] for x in d])[:,:,0]
def mf(h):
    r=h>>2; c=np.bincount(r,minlength=13); s=h&3
    pr=int(np.where(c==2)[0][0]); pk=[k for k in range(6) if r[k]==pr]
    si=sorted([k for k in range(6) if r[k]!=pr],key=lambda k:(-r[k],-h[k]))
    st=[k for k in si[1:] if s[k]==s[si[0]]]
    m={'pair':sp(*pk),'top2s':sp(si[0],si[1]),'low2s':sp(si[2],si[3]),'toplows':sp(si[0],si[3]),
       'top_lowsuit':sp(si[0],st[-1]) if st else sp(si[0],si[3]),'paircard_top':sp(pk[0],si[0])}
    f=dict(pr=pr,s1=int(r[si[0]]),s2=int(r[si[1]]),s3=int(r[si[2]]),s4=int(r[si[3]]),nhigh=int((r>=8).sum()),
           singles_ds=int(sorted(np.bincount(s[si],minlength=4))[-2]>=2), low2_suited=int(s[si[2]]==s[si[3]]),
           top2_suited=int(s[si[0]]==s[si[1]]), pair_over=int(pr>r[si[0]]))
    return m,f
OP=['pair','top2s','low2s','toplows','top_lowsuit','paircard_top']
fs=sorted(glob.glob('experiments/EXP-004/chunks/hands_*.npz')); H,V=load(fs[2:])
rows=[]
for h,v in zip(H,V):
    c=np.bincount(h>>2,minlength=13)
    if sorted(c[c>0].tolist())!=[1,1,1,1,2]: continue
    m,f=mf(h); f.update({k:v[m[k]] for k in OP}); rows.append(f)
df=pd.DataFrame(rows)
o2=np.load('experiments/EXP-004/split_oos.npz'); H2=o2['hands']; S2=o2['sv2']; rows=[]
for i,h in enumerate(H2):
    c=np.bincount(h>>2,minlength=13)
    if sorted(c[c>0].tolist())!=[1,1,1,1,2]: continue
    m,f=mf(h); f.update({k:S2[i,m[k]] for k in OP}); rows.append(f)
dv=pd.DataFrame(rows)
FE=['pr','s1','s2','s3','s4','nhigh','singles_ds','low2_suited','top2_suited','pair_over']
A=df[OP].values; F=df[FE].values
def best_leaf(idx): m=A[idx].mean(0); k=int(np.argmax(m)); return k, m[k]*len(idx)
def grow(idx, depth, minleaf=300):
    k,val=best_leaf(idx); node={'opt':OP[k],'n':len(idx)}
    if depth==0: return node,val
    bestgain=0;bs=None
    for j,fn in enumerate(FE):
        for thr in np.unique(F[idx,j])[:-1]:
            L=idx[F[idx,j]<=thr]; R=idx[F[idx,j]>thr]
            if len(L)<minleaf or len(R)<minleaf: continue
            g=best_leaf(L)[1]+best_leaf(R)[1]-val
            if g>bestgain: bestgain=g; bs=(j,thr,L,R)
    if bs is None: return node,val
    j,thr,L,R=bs; nl,vl=grow(L,depth-1,minleaf); nr,vr=grow(R,depth-1,minleaf)
    return {'feat':FE[j],'thr':thr,'L':nl,'R':nr,'n':len(idx)},vl+vr
def pred(node,row):
    while 'feat' in node: node=node['L'] if row[node['feat']]<=node['thr'] else node['R']
    return node['opt']
def show(node,ind=""):
    if 'feat' not in node: print(ind+f"-> {node['opt']} (n={node['n']})"); return
    print(ind+f"if {node['feat']} <= {node['thr']}:"); show(node['L'],ind+"   "); print(ind+"else:"); show(node['R'],ind+"   ")
print("n",len(df),"pair-only train",round(df.pair.mean(),4),"OOS",round(dv.pair.mean(),4))
b1=lambda d: np.where((d.pr<=8)&(d.s1==12)&(d.s2==11),d.top2s,d.pair)
print("B1 rule train",round(b1(df).mean(),4),"OOS",round(b1(dv).mean(),4))
for depth in [1,2,3]:
    tree,v=grow(np.arange(len(df)),depth); oos=np.mean([r[pred(tree,r)] for _,r in dv.iterrows()])
    print("depth",depth,"train",round(v/len(df),4),"OOS",round(oos,4)); show(tree)
