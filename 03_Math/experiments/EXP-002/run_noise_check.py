"""EXP-002 part 3: how much does Monte Carlo noise in the player's estimates understate player skill?
Same 50k hands, player estimates from 300/300/200 vs 1200/1200/800 rollouts."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.strategy2 import simulate_info, evaluate_structure, best_player_response
from uto.house_way import SIMPLE, WEIGHTED, simple_code
T = load(); NF, FL = tables(); args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)
H = simple_code(P=7, q=9, s=2); N = 50_000; SEED = 17_000_000
out = {}
for lab, roll in [("low", [300, 300, 200]), ("high", [1200, 1200, 800])]:
    info, o = simulate_info(N, SEED, SIMPLE, H, WEIGHTED, 0.75, np.array(roll), 810_000_000, *args)
    out[lab] = {}
    for st in [dict(pre=4, flop=2, base_win=1.0, river_fold=True), dict(pre=4, flop=2, base_win=0.0, river_fold=True),
               dict(pre=3, flop=1, base_win=0.5, river_fold=True)]:
        r = best_player_response(info, o, **st)   # in-sample on purpose: same selection for both
        out[lab][str(st)] = r["house_edge"]
        print(lab, st, round(r["house_edge"], 4), flush=True)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "results_noise_check.json"), "w"), indent=1)
