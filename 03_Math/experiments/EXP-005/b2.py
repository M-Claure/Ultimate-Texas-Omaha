import sys,glob; sys.path.insert(0,'src')
import numpy as np
from uto.player_split import book_split
fs=sorted(glob.glob('experiments/EXP-004/chunks/hands_*.npz'))
d=[np.load(f) for f in fs]; H=np.concatenate([x['hands'] for x in d]).astype(np.int64); V=np.concatenate([x['sv'] for x in d])[:,:,0]
o2=np.load('experiments/EXP-004/split_oos.npz'); H2=o2['hands']; S2=o2['sv2']; S1=o2['sv1']
for v in ["B1","B2"]:
    p=np.array([book_split(h,v) for h in H]); q=np.array([book_split(h,v) for h in H2])
    print(v,"36k",round(V[np.arange(len(H)),p].mean(),4),"OOS2k",round(S2[np.arange(len(H2)),q].mean(),4))
print("best biased 36k",round(V.max(1).mean(),4))
