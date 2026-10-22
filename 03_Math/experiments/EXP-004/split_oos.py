"""Out-of-sample test of split choices: the same 2,000 hands are re-solved with independent
random numbers. A split picked as best in run 1 is scored in run 2, so the comparison with simple
rules is unbiased (no 'best of noisy estimates' inflation)."""
import sys, os, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.optimal2 import solve_given2
from uto.house_way import SIMPLE, WEIGHTED, HOLDEM_FIRST, simple_code, choose_split

ST = np.array([[4, 2, 1, 0.0, 0]]); H = simple_code(P=7, q=9, s=2)
T = load(); NF, FL = tables(); A = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"]); args = A + (NF, FL)
d = [np.load(f) for f in sorted(glob.glob(os.path.join(HERE, "chunks", "hands_*.npz")))[:2]]
HANDS = np.concatenate([x["hands"] for x in d]).astype(np.int64)
SV1 = np.concatenate([x["sv"] for x in d])[:, :, 0]
_, SV2 = solve_given2(HANDS, 77_000_000, 2000, 4, 32, 2, 40, 400, ST, SIMPLE, H, *args)
SV2 = SV2[:, 0, :, 0]
np.savez_compressed(os.path.join(HERE, "split_oos.npz"), hands=HANDS, sv1=SV1, sv2=SV2)
b1 = SV1.argmax(1)
res = {}
def score(name, picks):
    v = SV2[np.arange(len(HANDS)), picks]
    res[name] = float(v.mean())
for name, (r, w) in {"H dealer rule": (SIMPLE, H), "H P=7 q=11": (SIMPLE, simple_code(P=7, q=11, s=2)),
                     "A v0.1": (HOLDEM_FIRST, 1.0), "C w=0.75": (WEIGHTED, 0.75)}.items():
    score(name, np.array([choose_split(h, r, w, False, *A) for h in HANDS]))
score("best in run 1 (optimal-ish)", b1)
base = res["H dealer rule"]
for k, v in res.items():
    print(f"{k:30s} EV {v:+.4f}  vs H {v-base:+.4f}")
json.dump(res, open(os.path.join(HERE, "split_oos.json"), "w"), indent=1)
