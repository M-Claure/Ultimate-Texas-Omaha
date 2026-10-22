"""Heads-up flat-bet simulator: one player vs the dealer, Base wager only, no raises/folds.

Every hand i is dealt from its own seed (seed + i), so different rule combinations are
compared on exactly the same cards (common random numbers -> precise paired comparisons).
"""
import numpy as np
from numba import njit, prange
from .evaluator import holdem_fast, omaha_fast, eval5
from .house_way import (PAIRS6, COMP6, choose_split, oracle_split, ORACLE)


@njit(parallel=True)
def simulate(n, seed, d_rule, d_w, p_rule, p_w, rollouts, oracle_seed,
             HEW, HET, OMW, OMT, NF, FL):
    """Returns per-hand arrays:
    outcome  +1 player win, 0 push, -1 player loss (flat bet, player's perspective)
    flags    bit0 Hold'em tie, bit1 Omaha tie, bit2 Hold'em tie where both play the board,
             bit3 player won Hold'em, bit4 player won Omaha
    dsplit   dealer split index (0..14)
    """
    outcome = np.zeros(n, np.int8)
    flags = np.zeros(n, np.int8)
    dsplit = np.zeros(n, np.int8)
    for i in prange(n):
        np.random.seed(seed + i)
        deck = np.arange(52)
        for k in range(17):
            r = k + np.random.randint(52 - k)
            deck[k], deck[r] = deck[r], deck[k]
        ph = deck[0:6].copy()
        dh = deck[6:12].copy()
        board = deck[12:17].copy()
        # player split (random rule uses the per-hand RNG stream after the deal)
        pp = choose_split(ph, p_rule, p_w, False, HEW, HET, OMW, OMT)
        if d_rule == ORACLE:
            np.random.seed(oracle_seed + i)
            sc = oracle_split(dh, rollouts, p_rule, p_w, HEW, HET, OMW, OMT, NF, FL)
            dp = 0
            for q in range(1, 15):
                if sc[q] > sc[dp]:
                    dp = q
        else:
            dp = choose_split(dh, d_rule, d_w, True, HEW, HET, OMW, OMT)
        dsplit[i] = dp
        p_he = holdem_fast(ph[PAIRS6[pp, 0]], ph[PAIRS6[pp, 1]], board, NF, FL)
        d_he = holdem_fast(dh[PAIRS6[dp, 0]], dh[PAIRS6[dp, 1]], board, NF, FL)
        pc = COMP6[pp]
        dc = COMP6[dp]
        p_om = omaha_fast(ph[pc[0]], ph[pc[1]], ph[pc[2]], ph[pc[3]], board, NF, FL)
        d_om = omaha_fast(dh[dc[0]], dh[dc[1]], dh[dc[2]], dh[dc[3]], board, NF, FL)
        f = 0
        wins = 0
        if p_he > d_he:
            wins += 1
            f |= 8
        elif p_he == d_he:
            f |= 1
            if p_he == eval5(board[0], board[1], board[2], board[3], board[4], NF, FL):
                f |= 4
        if p_om > d_om:
            wins += 1
            f |= 16
        elif p_om == d_om:
            f |= 2
        flags[i] = f
        outcome[i] = 1 if wins == 2 else (0 if wins == 1 else -1)
    return outcome, flags, dsplit


def summarize(outcome, flags):
    n = len(outcome)
    w = float(np.mean(outcome == 1))
    p = float(np.mean(outcome == 0))
    l = float(np.mean(outcome == -1))
    ev = float(np.mean(outcome))           # player EV per unit Base
    se = float(np.std(outcome) / np.sqrt(n))
    return {
        "hands": n, "win": w, "push": p, "loss": l,
        "house_edge": -ev, "house_edge_ci95": 1.96 * se,
        "he_tie": float(np.mean(flags & 1 > 0)), "om_tie": float(np.mean(flags & 2 > 0)),
        "he_board_tie": float(np.mean(flags & 4 > 0)),
        "p_he_win": float(np.mean(flags & 8 > 0)), "p_om_win": float(np.mean(flags & 16 > 0)),
    }


def paired_diff(o1, o2):
    """Difference in house edge (o1 - o2) with a 95% CI from paired hands."""
    d = -(o1.astype(np.float64) - o2.astype(np.float64))
    return float(d.mean()), float(1.96 * d.std() / np.sqrt(len(d)))
