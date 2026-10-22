"""EXP-002: generate per-hand decision info (P(win)/P(loss) at preflop, flop, river) with the
dealer using simple house way H. Saved to info_*.npz; structures are evaluated in analyze.py."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.strategy2 import simulate_info
from uto.house_way import SIMPLE, WEIGHTED, simple_code

SEED = 11_000_000; MC_SEED = 800_000_000
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300_000
ROLL = np.array([300, 300, 200])
H = simple_code(P=7, q=9, s=2)           # house way H (see EXP-002 report)
T = load(); NF, FL = tables()
args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)
t = time.time()
info, outcome = simulate_info(N, SEED, SIMPLE, H, WEIGHTED, 0.75, ROLL, MC_SEED, *args)
np.savez_compressed(os.path.join(os.path.dirname(__file__), f"info_H_{N}.npz"), info=info, outcome=outcome,
                    seed=SEED, mc_seed=MC_SEED, rollouts=ROLL, house_way_code=H)
print("done", N, round(time.time() - t), "s")
