import sys; sys.path.insert(0,'src')
import numpy as np, pandas as pd
from uto.features import flop_features
d=np.load('experiments/EXP-005/flop_data_b2.npz')
rows=[]
for h,p,f,e in zip(d['hands'],d['splits'],d['flop'],d['ej']):
    x=flop_features(h,p,f); x['d']=e[0]-e[1]; rows.append(x)
df=pd.DataFrame(rows); df.to_pickle('experiments/EXP-005/_flop_b2.pkl')
U=df.board_paired==0
he_real=np.where((~U)&(df.he_cat==1),0,df.he_cat); he_real=np.where((~U)&(df.he_cat==2)&(df.he_pair_hole==1),1,he_real)
best=np.where(df.d>0,df.d,0).mean()
F1=(df.om_cat>=3)|(U&(df.he_top_pair_plus==1)&((df.board_high>=6)|(df.he_cat>=2)))|((~U)&(he_real>=3))
F2=F1|((df.om_cat==2)&(df.he_pair_hole==1)&U)
X=pd.DataFrame({'he_top':((df.he_top_pair_plus==1)&(df.he_cat==1)&U),'he_2p':((df.he_cat==2)&(df.he_pair_hole==1)&U),
 'he_trips':(((df.he_cat>=3)&U)|((~U)&(df.he_cat>=3)&(df.he_pair_hole==1))),'he_pair_other':((df.he_cat==1)&(df.he_pair_hole==1)&(df.he_top_pair_plus==0)&U),
 'he_fd':df.he_fd==1,'om_trips':df.om_cat>=3,'om_2p':df.om_cat==2,'om_pair':df.om_cat==1,'om_top':df.om_top_pair==1,'om_fd':df.om_fd==1,'low_board':df.board_high<6}).astype(int)
pts=(5*X.he_2p+5*X.he_trips+4*X.he_top+1*X.he_pair_other+2*X.he_fd+5*X.om_trips+2*X.om_2p+1*X.om_pair+1*X.om_top+2*X.om_fd-1*X.low_board)
print("optimal flop gain per checked hand",round(best,4))
for name,m in [("F1",F1),("F2",F2),("points>=5",pts>=5),("points>=4",pts>=4)]:
    g=np.where(m,df.d,0).mean(); print(f"{name:10s} loss {best-g:.4f} raise {m.mean():.3f}")
