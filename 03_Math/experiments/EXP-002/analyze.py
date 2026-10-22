"""EXP-002 part 2: evaluate payout / raise structures on the stored decision info.
Player thresholds are chosen on the first half of the hands and evaluated on the second half
(avoids flattering the player by fitting to noise)."""
import sys, os, json, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
import numpy as np
from uto.strategy2 import evaluate_structure, best_player_response

path = sys.argv[1]
d = np.load(path)
info, outcome = d["info"], d["outcome"]
h = len(outcome) // 2
rows = []
for pre, flop, base_win, river_fold in itertools.product([4, 3, 2], [2, 1], [1.0, 0.5, 0.25, 0.0], [True, False]):
    if flop >= pre:
        continue
    st = dict(pre=pre, flop=flop, river=1, base_win=base_win, river_fold=river_fold)
    fit = best_player_response(info[:h], outcome[:h], **st)
    r = evaluate_structure(info[h:], outcome[h:], t_pre=fit["t_pre"], t_flop=fit["t_flop"], **st)
    r.update(st, t_pre=fit["t_pre"], t_flop=fit["t_flop"])
    rows.append(r)
    print(f"pre {pre}x flop {flop}x base_win {base_win:<4} fold {str(river_fold):5s} | edge {r['house_edge']:+.4f} ±{r['ci95']:.4f} "
          f"EoR {r['element_of_risk']:+.4f} avg bet {r['avg_total_bet']:.2f} | win {r['player_win_rate']:.3f} push {r['push_rate']:.3f} fold {r['fold']:.3f}", flush=True)
json.dump({"source": os.path.basename(path), "hands_eval": len(outcome) - h, "rows": rows},
          open(os.path.join(os.path.dirname(__file__), "results_structures.json"), "w"), indent=1)
