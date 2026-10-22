import sys,glob; sys.path.insert(0,'src')
import numpy as np, pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from uto.player_split import _PIDX
def sp(i,j): return _PIDX[tuple(sorted([i,j]))]
OPTS=['top2','low2','toplow','ace_lowsuit','top_lowsuit','2nd3rd','top3rd','2nd_low','3rd4th','4th5th']
def menu_feats(h):
    r=h>>2; o=sorted(range(6),key=lambda k:(-r[k],-h[k])); s=h&3
    m={'top2':sp(o[0],o[1]),'low2':sp(o[4],o[5]),'toplow':sp(o[0],o[5])}
    st=[k for k in o[1:] if s[k]==s[o[0]]]
    m['ace_lowsuit']=(sp(o[0],st[-1]) if st else sp(o[0],o[5]))
    m['top_lowsuit']=sp(o[0],st[-1]) if st else m['top2']
    m['2nd3rd']=sp(o[1],o[2]); m['top3rd']=sp(o[0],o[2]); m['2nd_low']=sp(o[1],o[5]); m['3rd4th']=sp(o[2],o[3]); m['4th5th']=sp(o[3],o[4])
    def ds(ks):
        c=np.bincount(s[ks],minlength=4); return int(sorted(c)[-2]>=2)
    f=dict(nhigh=int((r>=8).sum()), nQ=int((r>=10).sum()), top=int(r[o[0]]), second=int(r[o[1]]), third=int(r[o[2]]), fourth=int(r[o[3]]), low=int(r[o[5]]),
           tl_suited=int(s[o[0]]==s[o[5]]), top_has_suited=int(len(st)>0), ds_top4=ds([o[0],o[1],o[2],o[3]]),
           ds_last4=ds([o[2],o[3],o[4],o[5]]), low2_suited=int(s[o[4]]==s[o[5]]), top2_suited=int(s[o[0]]==s[o[1]]),
           span_top4=int(r[o[0]]-r[o[3]]), span_last4=int(r[o[2]]-r[o[5]]), nsuits=len(set(s.tolist())))
    return m,f
def load(chunks):
    d=[np.load(f) for f in chunks]; return np.concatenate([x['hands'] for x in d]).astype(np.int64), np.concatenate([x['sv'] for x in d])[:,:,0]
fs=sorted(glob.glob('experiments/EXP-004/chunks/hands_*.npz'))
H,V=load(fs[2:])
X=[];Y=[];W=[];VALS=[]
for h,v in zip(H,V):
    if len(set(h>>2))<6: continue
    m,f=menu_feats(h); vals=np.array([v[m[k]] for k in OPTS]); b=int(np.argmax(vals)); srt=np.sort(vals)
    X.append(f);Y.append(b);W.append(srt[-1]-srt[-2]+1e-6);VALS.append(vals)
X=pd.DataFrame(X);Y=np.array(Y);W=np.array(W);VALS=np.array(VALS)
o2=np.load('experiments/EXP-004/split_oos.npz'); H2=o2['hands']; S1=o2['sv1']; S2=o2['sv2']
X2=[];M2=[];I2=[]
for i,h in enumerate(H2):
    if len(set(h>>2))<6: continue
    m,f=menu_feats(h); X2.append(f);M2.append([m[k] for k in OPTS]);I2.append(i)
X2=pd.DataFrame(X2);M2=np.array(M2);I2=np.array(I2)
print("n train",len(Y),"OOS top2",round(S2[I2,M2[:,0]].mean(),4),"OOS best-run1 all15",round(S2[I2,S1[I2].argmax(1)].mean(),4))
print("menu-best in-sample (train)",round(VALS.max(1).mean(),4),"; label freq",np.bincount(Y,minlength=len(OPTS)))
for depth in [2,3,4,5,6]:
    t=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=80,random_state=0).fit(X,Y,sample_weight=W)
    p=t.predict(X2); print(depth,"train",round(VALS[np.arange(len(Y)),t.predict(X)].mean(),4),"OOS",round(S2[I2,M2[np.arange(len(I2)),p]].mean(),4))
    if depth==4: print(export_text(t,feature_names=list(X.columns),class_names=OPTS))
