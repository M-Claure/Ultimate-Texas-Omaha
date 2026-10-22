"""Which simple split rule should the PLAYER use? Regret vs the optimal split, measured on the
30,000 EXP-003 hands for the chosen structure (per-split optimal values, common random numbers)."""
import sys, os, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.house_way import choose_split, SIMPLE, WEIGHTED, HOLDEM_FIRST, simple_code

SI = 8   # structure index in EXP-003/structures.py: 4x/2x/1x, Base push on win, no fold
T = load(); A = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"])
fs = sorted(glob.glob(os.path.join(HERE, "..", "EXP-003", "chunks", "chunk_*.npz")))
H = np.concatenate([np.load(f)["hands"] for f in fs]); SV = np.concatenate([np.load(f)["sv"] for f in fs])[:, SI].astype(float)
best = SV.max(1)
rules = {"A v0.1 Hold'em-first": (HOLDEM_FIRST, 1.0)}
for P, q, s in [(0, 0, 0), (7, 9, 2), (7, 9, 0), (7, 10, 2), (6, 9, 2), (8, 9, 2), (8, 10, 2), (5, 9, 2), (7, 11, 2)]:
    rules[f"H-family P={P} q={q} s={s}"] = (SIMPLE, simple_code(P=P, q=q, s=s))
for w in (0.5, 0.75, 1.0, 1.25):
    rules[f"C weighted w={w} (not human)"] = (WEIGHTED, w)
res = {}
for name, (r, w) in rules.items():
    reg = np.array([best[i] - SV[i, choose_split(H[i].astype(np.int64), r, w, False, *A)] for i in range(len(H))])
    res[name] = (float(reg.mean()), float(1.96 * reg.std() / np.sqrt(len(reg))), float(np.mean(reg < 1e-9)))
    print(f"{name:34s} regret {reg.mean()*100:.2f}% ±{1.96*reg.std()/np.sqrt(len(reg))*100:.2f}  same as optimal {np.mean(reg<1e-9):.2f}", flush=True)
json.dump(res, open(os.path.join(HERE, "split_rule_regret.json"), "w"), indent=1)
