"""Play the strategy book (B1 split, preflop R2, flop F1, always call 1x at river) against the
dealer (House Way H) on real random deals and measure the house edge. Rule-based decisions use
only the player's own information, so this is an unbiased estimate for a human following the book.
Usage: python3 book_sim.py N_HANDS WORKERS"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import numpy as np
from multiprocessing import Pool


def flop_raise(f):
    U = f["board_paired"] == 0
    he_real = f["he_cat"]
    if not U and f["he_cat"] == 1:
        he_real = 0
    if not U and f["he_cat"] == 2 and f["he_pair_hole"] == 1:
        he_real = 1
    return (f["om_cat"] >= 3) or (U and f["he_top_pair_plus"] == 1 and (f["board_high"] >= 6 or f["he_cat"] >= 2)) or ((not U) and he_real >= 3)


def worker(args):
    seed, n = args
    from uto.equity import load
    from uto.evaluator import tables, holdem_fast, omaha_fast
    from uto.house_way import choose_split, SIMPLE, simple_code, PAIRS6, COMP6
    from uto.player_split import book_split
    from uto.book_rules import preflop_raise
    from uto.features import flop_features
    T = load(); NF, FL = tables(); A = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"])
    Hcode = simple_code(P=7, q=9, s=2)
    rng = np.random.default_rng(seed)
    res = np.zeros(n); bet = np.zeros(n); act = np.zeros(n, np.int8); oc = np.zeros(n, np.int8)
    for i in range(n):
        d = rng.permutation(52).astype(np.int64)
        ph, dh, board = d[:6], d[6:12], d[12:17]
        pp = book_split(ph)
        if preflop_raise(ph, pp):
            R = 4; act[i] = 4
        elif flop_raise(flop_features(ph, pp, board[:3])):
            R = 2; act[i] = 2
        else:
            R = 1; act[i] = 1
        dp = choose_split(dh, SIMPLE, Hcode, True, *A)
        pc, dc = COMP6[pp], COMP6[dp]
        w = int(holdem_fast(ph[PAIRS6[pp, 0]], ph[PAIRS6[pp, 1]], board, NF, FL) > holdem_fast(dh[PAIRS6[dp, 0]], dh[PAIRS6[dp, 1]], board, NF, FL))
        w += int(omaha_fast(ph[pc[0]], ph[pc[1]], ph[pc[2]], ph[pc[3]], board, NF, FL) > omaha_fast(dh[dc[0]], dh[dc[1]], dh[dc[2]], dh[dc[3]], board, NF, FL))
        o = 1 if w == 2 else (0 if w == 1 else -1)
        oc[i] = o
        res[i] = R if o == 1 else (0 if o == 0 else -(1 + R))   # Base pushes on a win
        bet[i] = 1 + R
    return res, bet, act, oc


if __name__ == "__main__":
    N, Wk = int(sys.argv[1]), int(sys.argv[2])
    t = time.time()
    with Pool(Wk) as pool:
        parts = pool.map(worker, [(61_000_000 + k, N // Wk) for k in range(Wk)])
    res = np.concatenate([p[0] for p in parts]); bet = np.concatenate([p[1] for p in parts])
    act = np.concatenate([p[2] for p in parts]); oc = np.concatenate([p[3] for p in parts])
    out = dict(hands=len(res), house_edge=float(-res.mean()), ci95=float(1.96 * res.std() / np.sqrt(len(res))),
               element_of_risk=float(-res.mean() / bet.mean()), avg_total_bet=float(bet.mean()), sd=float(res.std()),
               raise4=float((act == 4).mean()), raise2=float((act == 2).mean()), call1=float((act == 1).mean()),
               win=float((oc == 1).mean()), push=float((oc == 0).mean()), loss=float((oc == -1).mean()),
               by_action={str(a): dict(freq=float((act == a).mean()), win=float((oc[act == a] == 1).mean()),
                                       push=float((oc[act == a] == 0).mean()), loss=float((oc[act == a] == -1).mean()))
                          for a in (4, 2, 1)},
               seconds=time.time() - t)
    json.dump(out, open(os.path.join(HERE, "book_sim_results.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))
