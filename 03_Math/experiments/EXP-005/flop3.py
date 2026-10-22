import pandas as pd, numpy as np
df=pd.read_pickle('experiments/EXP-005/_flop_b2.pkl')
U=df.board_paired==0
he_real=np.where((~U)&(df.he_cat==1),0,df.he_cat); he_real=np.where((~U)&(df.he_cat==2)&(df.he_pair_hole==1),1,he_real)
best=np.where(df.d>0,df.d,0).mean()
F2=(df.om_cat>=3)|(U&(df.he_top_pair_plus==1)&((df.board_high>=6)|(df.he_cat>=2)))|((~U)&(he_real>=3))|((df.om_cat==2)&(df.he_pair_hole==1)&U)
cands={
 "F2 + HE top pair on low flop if Om pair": F2|(U&(df.he_top_pair_plus==1)&(df.om_cat>=1)),
 "F2 + HE fd & Om 2pair": F2|((df.he_fd==1)&(df.om_cat==2)),
 "F2 + Om two pair w/ top pair": F2|((df.om_cat==2)&(df.om_top_pair==1)),
 "F2 + HE top pair+ & Om fd": F2|((df.he_top_pair_plus==1)&(df.om_fd==1)),
 "F2 + paired flop HE 2p(real) & Om 2p": F2|((~U)&(he_real>=1)&(df.om_cat>=2)),
}
g=np.where(F2,df.d,0).mean(); print("F2 loss",round(best-g,4))
for k,m in cands.items():
    g=np.where(m,df.d,0).mean(); print(f"{k:45s} loss {best-g:.4f}")
