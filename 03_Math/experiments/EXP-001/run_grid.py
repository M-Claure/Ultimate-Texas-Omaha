"""EXP-001 part 2: dealer weight w vs player weight w (both use rule C), flat bet.
Looks for the dealer weight that holds up best against the player's best response."""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.sim import simulate, summarize
from uto.house_way import WEIGHTED, HOLDEM_FIRST

SEED = 3_000_000; N = 1_000_000
T = load(); NF, FL = tables()
args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)
dws = [("A", HOLDEM_FIRST, 1.0)] + [(f"C{w}", WEIGHTED, w) for w in (0.25, 0.4, 0.5, 0.6, 0.75)]
pws = [0.25, 0.4, 0.5, 0.6, 0.75, 1.0]
grid = {}
for dn, dr, dw in dws:
    for pw in pws:
        o, f, _ = simulate(N, SEED, dr, dw, WEIGHTED, pw, 0, 0, *args)
        s = summarize(o, f)
        grid[f"{dn}|P{pw}"] = s
        print(f"dealer {dn:6s} player w={pw:<5} edge {s['house_edge']:+.4f} ±{s['house_edge_ci95']:.4f}", flush=True)
json.dump({"seed": SEED, "hands": N, "rules_version": "v0.2", "grid": grid},
          open(os.path.join(os.path.dirname(__file__), "results_grid.json"), "w"), indent=1)
