"""EXP-001 part 3: preview of the house edge WITH raises, using the simple strategy S1
(src/uto/strategy.py). S1 is not optimal, so these are upper bounds on the house edge."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from uto.equity import load
from uto.evaluator import tables
from uto.strategy import simulate_s1, evaluate_s1
from uto.house_way import WEIGHTED, HOLDEM_FIRST

SEED = 5_000_000; MC_SEED = 700_000_000; N = 100_000; PRE, RIV = 300, 200
T = load(); NF, FL = tables()
args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)
out = {"seed": SEED, "mc_seed": MC_SEED, "hands": N, "pre_rollouts": PRE, "river_rollouts": RIV,
       "rules_version": "v0.2", "player_split": "C w=0.75", "runs": {}}
for name, dr, dw in [("A Hold'em-first (v0.1)", HOLDEM_FIRST, 1.0), ("C Weighted w=0.5", WEIGHTED, 0.5)]:
    t = time.time()
    a = simulate_s1(N, SEED, dr, dw, WEIGHTED, 0.75, PRE, RIV, MC_SEED, *args)
    out["runs"][name] = [evaluate_s1(*a, th) for th in (0.0, 0.05, 0.1, 0.15, 0.2, 0.3)]
    for r in out["runs"][name]:
        print(f"{name:24s} thr {r['threshold']:.2f}: house edge {r['house_edge']:+.4f} ±{r['house_edge_ci95']:.4f} "
              f"EoR {r['element_of_risk']:+.4f} raise4 {r['raise4_rate']:.3f} fold {r['fold_rate']:.3f}", flush=True)
    print(round(time.time() - t), "s")
json.dump(out, open(os.path.join(os.path.dirname(__file__), "results_raise_preview.json"), "w"), indent=1)
