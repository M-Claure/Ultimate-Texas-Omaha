"""Exact river probabilities by full enumeration of the dealer's 6 cards (validation only)."""
import numpy as np
from numba import njit
from .evaluator import holdem_fast, omaha_fast
from .house_way import PAIRS6, COMP6, choose_split


@njit(cache=False)
def exact_river(ph, pp, board, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL):
    excl = np.zeros(52, np.bool_)
    for k in range(6):
        excl[ph[k]] = True
    for k in range(5):
        excl[board[k]] = True
    deck = np.empty(41, np.int64)
    j = 0
    for c in range(52):
        if not excl[c]:
            deck[j] = c
            j += 1
    pc = COMP6[pp]
    pHE = holdem_fast(ph[PAIRS6[pp, 0]], ph[PAIRS6[pp, 1]], board, NF, FL)
    pOM = omaha_fast(ph[pc[0]], ph[pc[1]], ph[pc[2]], ph[pc[3]], board, NF, FL)
    dh = np.empty(6, np.int64)
    w = 0
    l = 0
    n = 0
    for a in range(41):
        for b in range(a + 1, 41):
            for c in range(b + 1, 41):
                for d in range(c + 1, 41):
                    for e in range(d + 1, 41):
                        for f in range(e + 1, 41):
                            dh[0] = deck[a]; dh[1] = deck[b]; dh[2] = deck[c]
                            dh[3] = deck[d]; dh[4] = deck[e]; dh[5] = deck[f]
                            dp = choose_split(dh, d_rule, d_w, True, HEW, HET, OMW, OMT)
                            dc = COMP6[dp]
                            dHE = holdem_fast(dh[PAIRS6[dp, 0]], dh[PAIRS6[dp, 1]], board, NF, FL)
                            dOM = omaha_fast(dh[dc[0]], dh[dc[1]], dh[dc[2]], dh[dc[3]], board, NF, FL)
                            ww = (1 if pHE > dHE else 0) + (1 if pOM > dOM else 0)
                            if ww == 2:
                                w += 1
                            elif ww == 0:
                                l += 1
                            n += 1
    return w / n, l / n, n
