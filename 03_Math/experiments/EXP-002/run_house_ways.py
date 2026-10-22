"""EXP-002 part 1: dealer-friendly house ways vs v0.1 (A), weighted rule C and the oracle (flat bet).
Each rule is tested against three reference players on the same 2M deals."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.sim import simulate, summarize, paired_diff
from uto.house_way import HOLDEM_FIRST, WEIGHTED, SIMPLE, ORACLE, simple_code

SEED = 13_000_000; N = 2_000_000; N_OR = 100_000; OR_SEED = 950_000_000
T = load(); NF, FL = tables()
args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)
rules = [
    ("A v0.1 Hold'em-first", HOLDEM_FIRST, 1.0),
    ("S1 pair->HE else top two", SIMPLE, simple_code()),
    ("S2 + small-pair switch (2-8 / J+)", SIMPLE, simple_code(P=7, q=9)),
    ("H  = S2 + keep Omaha suited", SIMPLE, simple_code(P=7, q=9, s=2)),
    ("C weighted w=0.5 (reference)", WEIGHTED, 0.5),
]
players = [("player C w=0.75", WEIGHTED, 0.75), ("player C w=1.0", WEIGHTED, 1.0),
           ("player A v0.1", HOLDEM_FIRST, 1.0)]
res = {"seed": SEED, "hands": N, "rules_version": "v0.2", "rows": []}
for pn, pr, pw in players:
    ref = simulate(N, SEED, WEIGHTED, 0.5, pr, pw, 0, 0, *args)[0]
    for dn, dr, dw in rules:
        o, f, _ = simulate(N, SEED, dr, dw, pr, pw, 0, 0, *args)
        s = summarize(o, f); s.update(dealer=dn, player=pn)
        s["minus_C"], s["minus_C_ci95"] = paired_diff(o, ref)
        res["rows"].append(s)
        print(f"{pn:16s} | {dn:36s} | edge {s['house_edge']:+.4f} ±{s['house_edge_ci95']:.4f} | vs C {s['minus_C']:+.4f} ±{s['minus_C_ci95']:.4f}", flush=True)
# oracle check vs H on the same 100k deals
oD = simulate(N_OR, SEED, ORACLE, 1.0, WEIGHTED, 0.75, 300, OR_SEED, *args)[0]
oH = simulate(N_OR, SEED, SIMPLE, simple_code(P=7, q=9, s=2), WEIGHTED, 0.75, 0, 0, *args)[0]
res["oracle_minus_H"] = paired_diff(oD, oH)
print("oracle - H:", res["oracle_minus_H"])
json.dump(res, open(os.path.join(os.path.dirname(__file__), "results_house_ways.json"), "w"), indent=1)
