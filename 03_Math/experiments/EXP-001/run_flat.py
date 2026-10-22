"""EXP-001 part 1: dealer house-way tournament, flat Base bet (no raises, no folds).

Run from 03_Math/:  python3 experiments/EXP-001/run_flat.py
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.sim import simulate, summarize, paired_diff
from uto.house_way import RANDOM, HOLDEM_FIRST, OMAHA_FIRST, WEIGHTED, ORACLE, RULE_NAMES

SEED = 1_000_000          # deal seeds: SEED + hand index
ORACLE_SEED = 900_000_000
N = 2_000_000             # hands per heuristic matchup
N_ORACLE = 100_000        # hands for the oracle (expensive)
ROLLOUTS = 300

T = load(); NF, FL = tables()
args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)

dealer_rules = [("Random", RANDOM, 1.0), ("A Hold'em-first (v0.1)", HOLDEM_FIRST, 1.0),
                ("B Omaha-first", OMAHA_FIRST, 1.0)]
dealer_rules += [(f"C Weighted w={w}", WEIGHTED, w) for w in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)]
player_rules = [("Player A Hold'em-first", HOLDEM_FIRST, 1.0), ("Player B Omaha-first", OMAHA_FIRST, 1.0),
                ("Player C Weighted w=1", WEIGHTED, 1.0)]

results = {"seed": SEED, "hands": N, "rules_version": "v0.2", "matchups": []}
t0 = time.time()
for pname, pr, pw in player_rules:
    base = None
    for dname, dr, dw in dealer_rules:
        o, f, _ = simulate(N, SEED, dr, dw, pr, pw, 0, 0, *args)
        s = summarize(o, f)
        if dname.startswith("A "):
            base = o
        s.update(dealer=dname, player=pname)
        if base is not None and not dname.startswith("A "):
            s["edge_vs_A"], s["edge_vs_A_ci95"] = paired_diff(o, base)
        results["matchups"].append(s)
        print(f"{pname:24s} | {dname:24s} | edge {s['house_edge']:+.4f} ±{s['house_edge_ci95']:.4f} "
              f"| W {s['win']:.3f} P {s['push']:.3f} L {s['loss']:.3f}", flush=True)

# Oracle (option D) vs player C, compared on the same 100k deals with the best heuristic
results["oracle"] = []
for pname, pr, pw in player_rules[2:]:
    o_d, f_d, _ = simulate(N_ORACLE, SEED, ORACLE, 1.0, pr, pw, ROLLOUTS, ORACLE_SEED, *args)
    sd = summarize(o_d, f_d); sd.update(dealer=f"D Oracle ({ROLLOUTS} rollouts)", player=pname)
    comps = {}
    for dname, dr, dw in dealer_rules:
        o, f, _ = simulate(N_ORACLE, SEED, dr, dw, pr, pw, 0, 0, *args)
        comps[dname] = paired_diff(o_d, o)
    sd["oracle_minus_rule"] = comps
    results["oracle"].append(sd)
    print(f"{pname:24s} | D Oracle | edge {sd['house_edge']:+.4f} ±{sd['house_edge_ci95']:.4f} "
          f"| W {sd['win']:.3f} P {sd['push']:.3f} L {sd['loss']:.3f}")
    for k, (m, c) in comps.items():
        print(f"     oracle - {k:24s}: {m:+.4f} ±{c:.4f}")
results["seconds"] = time.time() - t0
out = os.path.join(os.path.dirname(__file__), "results_flat.json")
json.dump(results, open(out, "w"), indent=1)
print("saved", out, round(results["seconds"]), "s")
