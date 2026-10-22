"""EXP-004 data: per-hand optimal values of every split (raise-4x value and check value) for the
chosen structure 4x/2x/1x, Base pushes on a win, no river fold. Used to derive the player's
split and preflop rules and to measure what simplified rules cost."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.optimal2 import solve_many2
from uto.house_way import SIMPLE, simple_code

ST = np.array([[4, 2, 1, 0.0, 0]])
SEED = 41_000_000; CHUNK = 1000
PARAMS = dict(NLB=2000, NLD=4, M=32, K=2, D=40, NFB=400)
H = simple_code(P=7, q=9, s=2)
T = load(); NF, FL = tables(); args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)
outdir = os.path.join(HERE, "chunks"); os.makedirs(outdir, exist_ok=True)
for c in range(int(sys.argv[1]), int(sys.argv[2])):
    f = os.path.join(outdir, f"hands_{c:03d}.npz")
    if os.path.exists(f):
        continue
    t = time.time()
    hands, out, sv = solve_many2(CHUNK, SEED + c * CHUNK, *PARAMS.values(), ST, SIMPLE, H, *args)
    np.savez_compressed(f, hands=hands, out=out[:, 0], sv=sv[:, 0], seed=SEED + c * CHUNK)
    print(f"chunk {c} {time.time() - t:.0f}s", flush=True)
