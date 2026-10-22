"""EXP-003 production run: optimal-play EV for every structure in structures.py, dealer House Way H.
Writes one file per chunk of hands so the run can be resumed. Usage:
  python3 experiments/EXP-003/run_optimal.py START_CHUNK END_CHUNK
"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src")); sys.path.insert(0, HERE)
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.optimal2 import solve_many2
from uto.house_way import SIMPLE, simple_code
from structures import ST

SEED = 31_000_000          # hand i of chunk c uses seed SEED + c*CHUNK + i
CHUNK = 1000
PARAMS = dict(NLB=2000, NLD=4, M=24, K=8, D=160, NFB=200)
H = simple_code(P=7, q=9, s=2)
T = load(); NF, FL = tables(); args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)
outdir = os.path.join(HERE, "chunks"); os.makedirs(outdir, exist_ok=True)
a, b = int(sys.argv[1]), int(sys.argv[2])
for c in range(a, b):
    f = os.path.join(outdir, f"chunk_{c:03d}.npz")
    if os.path.exists(f):
        continue
    t = time.time()
    hands, out, sv = solve_many2(CHUNK, SEED + c * CHUNK, *PARAMS.values(), ST, SIMPLE, H, *args)
    np.savez_compressed(f, hands=hands, out=out.astype(np.float32), sv=sv[..., 0].astype(np.float32),
                        seed=SEED + c * CHUNK, params=np.array(list(PARAMS.values())))
    print(f"chunk {c} done in {time.time() - t:.0f}s", flush=True)
