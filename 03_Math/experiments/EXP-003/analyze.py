"""Aggregate EXP-003 chunks: house edge under optimal play (bracket), with a control variate.

Control variate: features of the player's hand computed from the equity tables (Hold'em and Omaha
win-equity of the split maximising HE + 0.75*Omaha). Their population means are computed from
4,000,000 random hands, so subtracting the regression on these features removes most of the
hand-to-hand variance without biasing the estimate.
"""
import sys, os, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src")); sys.path.insert(0, HERE)
import numpy as np
from numba import njit, prange
from uto.equity import load, idx2, idx4
from uto.house_way import PAIRS6, COMP6
from structures import ST, label

T = load(); HEW, OMW = T["he_win"], T["om_win"]


@njit
def _feat(h, HEW, OMW):
    best = -1.0; bh = 0.0; bo = 0.0
    for p in range(15):
        c = COMP6[p]
        he = HEW[idx2(h[PAIRS6[p, 0]], h[PAIRS6[p, 1]])]
        om = OMW[idx4(h[c[0]], h[c[1]], h[c[2]], h[c[3]])]
        if he + 0.75 * om > best:
            best = he + 0.75 * om; bh = he; bo = om
    x = np.empty(7)
    x[0] = bh; x[1] = bo; x[2] = bh * bo; x[3] = bh * bh; x[4] = bo * bo
    x[5] = max(bh + bo - 1.0, 0.0) ** 2; x[6] = bh * bh * bo
    return x


@njit(parallel=True)
def feats(H, HEW, OMW):
    X = np.zeros((H.shape[0], 7))
    for i in prange(H.shape[0]):
        X[i] = _feat(H[i], HEW, OMW)
    return X


@njit(parallel=True)
def pop_means(n, seed, HEW, OMW):
    S = np.zeros((n, 7))
    for i in prange(n):
        np.random.seed(seed + i)
        deck = np.arange(52)
        for k in range(6):
            r = k + np.random.randint(52 - k)
            deck[k], deck[r] = deck[r], deck[k]
        S[i] = _feat(deck[:6].copy(), HEW, OMW)
    out = np.zeros(7)
    for i in range(n):
        out += S[i]
    return out / n


def cv_mean(y, X, mu):
    A = np.c_[np.ones(len(y)), X]
    coef = np.linalg.lstsq(A, y, rcond=None)[0]
    adj = y - (X - mu) @ coef[1:]
    return float(adj.mean()), float(1.96 * adj.std() / np.sqrt(len(y))), float(1 - adj.var() / y.var())


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(HERE, "chunks", "chunk_*.npz")))
    H = np.concatenate([np.load(f)["hands"] for f in files])
    OUT = np.concatenate([np.load(f)["out"] for f in files]).astype(np.float64)
    X = feats(H, HEW, OMW)
    mu = pop_means(4_000_000, 999_000_000, HEW, OMW)
    rows = []
    for si in range(len(ST)):
        o = OUT[:, si, :]
        I, Ici, r2 = cv_mean(o[:, 0], X, mu)
        P, Pci, _ = cv_mean(o[:, 1], X, mu)
        mid = 0.5 * (I + P)
        ebet = float(o[:, 6].mean()); er2 = float(o[:, 9].mean())
        rows.append(dict(structure=label(ST[si]), R=list(map(float, ST[si])), hands=len(o),
                         house_edge_low=-I, house_edge_high=-P, house_edge_mid=-mid,
                         ci95=max(Ici, Pci), cv_r2=r2,
                         element_of_risk_mid=-mid / ebet, avg_total_bet=ebet,
                         sd=float(np.sqrt(er2 - mid ** 2)),
                         p_raise_pre=float(o[:, 3].mean()),
                         p_raise_flop=float(((1 - o[:, 3]) * o[:, 4]).mean()),
                         p_fold=float(((1 - o[:, 3]) * o[:, 5]).mean()),
                         p_win=float(o[:, 7].mean()), p_loss_incl_fold=float(o[:, 8].mean())))
        r = rows[-1]
        print(f"{r['structure']:45s} house edge {r['house_edge_mid']*100:+6.2f}%  [{r['house_edge_low']*100:+.2f}, {r['house_edge_high']*100:+.2f}] ±{r['ci95']*100:.2f}  "
              f"EoR {r['element_of_risk_mid']*100:+.2f}%  bet {ebet:.2f}  sd {r['sd']:.2f}")
    json.dump({"hands": len(H), "population_feature_means": mu.tolist(), "rows": rows},
              open(os.path.join(HERE, "results_optimal.json"), "w"), indent=1)
