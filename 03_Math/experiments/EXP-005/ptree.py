import sys,glob; sys.path.insert(0,'src')
import numpy as np, pandas as pd
exec(open('experiments/EXP-005/np_search.py').read().split("def rule(")[0])
FE=['nhigh','nQ','top','second','third','fourth','low','tl_suited','top_has_suited','ds_top4','ds_last4','low2_suited','top2_suited','span_top4','span_last4','nsuits']
OP=['top2','low2','toplow','ace_lowsuit','2nd3rd','top3rd','2nd_low','3rd4th','4th5th']
A=df[OP].values; F=df[FE].values
def best_leaf(idx): m=A[idx].mean(0); k=int(np.argmax(m)); return k, m[k]*len(idx)
def grow(idx, depth, minleaf=300):
    k,val=best_leaf(idx)
    node={'opt':OP[k],'n':len(idx)}
    if depth==0: return node,val
    bestgain=0;bs=None
    for j,fn in enumerate(FE):
        for thr in np.unique(F[idx,j])[:-1]:
            L=idx[F[idx,j]<=thr]; R=idx[F[idx,j]>thr]
            if len(L)<minleaf or len(R)<minleaf: continue
            g=best_leaf(L)[1]+best_leaf(R)[1]-val
            if g>bestgain: bestgain=g; bs=(j,thr,L,R)
    if bs is None: return node,val
    j,thr,L,R=bs
    nl,vl=grow(L,depth-1,minleaf); nr,vr=grow(R,depth-1,minleaf)
    return {'feat':FE[j],'thr':thr,'L':nl,'R':nr,'n':len(idx)},vl+vr
def pred(node,row):
    while 'feat' in node: node=node['L'] if row[node['feat']]<=node['thr'] else node['R']
    return node['opt']
def show(node,ind=""):
    if 'feat' not in node: print(ind+f"-> {node['opt']} (n={node['n']})"); return
    print(ind+f"if {node['feat']} <= {node['thr']}:"); show(node['L'],ind+"   ")
    print(ind+"else:"); show(node['R'],ind+"   ")
idx=np.arange(len(df))
for depth in [2,3,4]:
    tree,v=grow(idx,depth)
    oos=np.mean([r[pred(tree,r)] for _,r in dv.iterrows()])
    print("depth",depth,"train",round(v/len(df),4),"OOS",round(oos,4))
    if depth==3: show(tree)
