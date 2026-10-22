"""Datasets for deriving the player strategy book (flop and river decision points)."""
import numpy as np
from numba import njit, prange
from .house_way import choose_split, PAIRS6
from .evaluator import holdem_fast, omaha_pair
from .optimal import _board_counts
from .optimal2 import _joint


@njit(parallel=True)
def river_data(n, seed, p_rule, p_w, D, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL):
    """Random player hand (split by p_rule) + full board; exact-ish P(win)/P(loss) from D dealers."""
    HANDS = np.zeros((n, 6), np.int64)
    BOARD = np.zeros((n, 5), np.int64)
    SPL = np.zeros(n, np.int64)
    PWL = np.zeros((n, 2))
    for i in prange(n):
        np.random.seed(seed + i)
        deck = np.arange(52)
        for k in range(11):
            r = k + np.random.randint(52 - k)
            deck[k], deck[r] = deck[r], deck[k]
        ph = deck[0:6].copy()
        pp = choose_split(ph, p_rule, p_w, False, HEW, HET, OMW, OMT)
        rest = np.empty(46, np.int64)
        for k in range(5):
            rest[k] = deck[6 + k]
        for k in range(41):
            rest[5 + k] = deck[11 + k]
        board = rest[0:5].copy()
        he_p = np.empty(15, np.int64)
        om_p = np.empty(15, np.int64)
        for p in range(15):
            he_p[p] = holdem_fast(ph[PAIRS6[p, 0]], ph[PAIRS6[p, 1]], board, NF, FL)
            om_p[p] = omaha_pair(ph[PAIRS6[p, 0]], ph[PAIRS6[p, 1]], board, NF, FL)
        win = np.zeros(15, np.int64)
        loss = np.zeros(15, np.int64)
        _board_counts(rest, D, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, he_p, om_p, win, loss)
        HANDS[i] = ph
        BOARD[i] = board
        SPL[i] = pp
        PWL[i, 0] = win[pp] / D
        PWL[i, 1] = loss[pp] / D
    return HANDS, BOARD, SPL, PWL


@njit(parallel=True)
def flop_data(n, seed, p_rule, p_w, NJ, K, D, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL):
    """Random player hand + flop. Returns E[pw], E[pl] given the flop from NJ joint samples
    (NJ/4 boards x 4 dealers) and per-board (pw, pl) for K river boards (D dealers each) so
    the river fold option can be valued for any payout structure."""
    HANDS = np.zeros((n, 6), np.int64)
    FLOP = np.zeros((n, 3), np.int64)
    SPL = np.zeros(n, np.int64)
    EJ = np.zeros((n, 2))
    BWL = np.zeros((n, K, 2))
    for i in prange(n):
        np.random.seed(seed + i)
        deck = np.arange(52)
        for k in range(9):
            r = k + np.random.randint(52 - k)
            deck[k], deck[r] = deck[r], deck[k]
        ph = deck[0:6].copy()
        pp = choose_split(ph, p_rule, p_w, False, HEW, HET, OMW, OMT)
        rest = np.empty(46, np.int64)
        for k in range(46):
            rest[k] = deck[6 + k]
        W = np.zeros(15, np.int64)
        L = np.zeros(15, np.int64)
        nj = _joint(rest, 3, NJ // 4, 4, ph, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, W, L)
        EJ[i, 0] = W[pp] / nj
        EJ[i, 1] = L[pp] / nj
        he_p = np.empty(15, np.int64)
        om_p = np.empty(15, np.int64)
        win = np.zeros(15, np.int64)
        loss = np.zeros(15, np.int64)
        for kk in range(K):
            for k in range(3, 5):
                r = k + np.random.randint(46 - k)
                rest[k], rest[r] = rest[r], rest[k]
            board = rest[0:5]
            for p in range(15):
                he_p[p] = holdem_fast(ph[PAIRS6[p, 0]], ph[PAIRS6[p, 1]], board, NF, FL)
                om_p[p] = omaha_pair(ph[PAIRS6[p, 0]], ph[PAIRS6[p, 1]], board, NF, FL)
            _board_counts(rest, D, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, he_p, om_p, win, loss)
            BWL[i, kk, 0] = win[pp] / D
            BWL[i, kk, 1] = loss[pp] / D
        HANDS[i] = ph
        FLOP[i] = rest[0:3]
        SPL[i] = pp
    return HANDS, FLOP, SPL, EJ, BWL


@njit(parallel=True)
def flop_given(HANDS, SPLITS, seed, NJB, NJD, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL):
    """For given player hands and splits: draw a random flop, then estimate P(win both) and
    P(lose both) given the flop from NJB turn/river boards x NJD dealer hands."""
    n = HANDS.shape[0]
    FLOP = np.zeros((n, 3), np.int64)
    EJ = np.zeros((n, 2))
    for i in prange(n):
        np.random.seed(seed + i)
        ph = HANDS[i].copy()
        rest = np.empty(46, np.int64)
        j = 0
        for c in range(52):
            hit = False
            for k in range(6):
                if ph[k] == c:
                    hit = True
            if not hit:
                rest[j] = c
                j += 1
        for k in range(3):
            r = k + np.random.randint(46 - k)
            rest[k], rest[r] = rest[r], rest[k]
        W = np.zeros(15, np.int64)
        L = np.zeros(15, np.int64)
        nj = _joint(rest, 3, NJB, NJD, ph, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, W, L)
        pp = SPLITS[i]
        EJ[i, 0] = W[pp] / nj
        EJ[i, 1] = L[pp] / nj
        FLOP[i] = rest[0:3]
    return FLOP, EJ
