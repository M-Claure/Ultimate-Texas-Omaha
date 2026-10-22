"""Simple (not optimal) player raise/fold strategy, used to bound the house edge with raises.

Strategy S1 ("simple raiser"):
  * Preflop: estimate the hand's EV by Monte Carlo vs the dealer house way.
    Raise 4x if EV_pre > threshold; otherwise check (never raise 2x on the flop).
  * River (if not raised): estimate EV of the now-known hands; call 1x if EV_river > -0.5
    (calling stakes 2 units: 2*EV > -1), otherwise fold.
Because this player is not optimal, the house edge it faces is an UPPER bound on the house edge
against an optimal player.

simulate_s1 stores the per-hand ingredients (EV_pre, EV_river, actual outcome) so that every
threshold can be evaluated afterwards on the same hands.
"""
import numpy as np
from numba import njit, prange
from .evaluator import holdem_fast, omaha_fast
from .house_way import PAIRS6, COMP6, choose_split


@njit(cache=True)
def _outcome(ph, pp, dh, dp, board, NF, FL):
    p_he = holdem_fast(ph[PAIRS6[pp, 0]], ph[PAIRS6[pp, 1]], board, NF, FL)
    d_he = holdem_fast(dh[PAIRS6[dp, 0]], dh[PAIRS6[dp, 1]], board, NF, FL)
    pc = COMP6[pp]
    dc = COMP6[dp]
    p_om = omaha_fast(ph[pc[0]], ph[pc[1]], ph[pc[2]], ph[pc[3]], board, NF, FL)
    d_om = omaha_fast(dh[dc[0]], dh[dc[1]], dh[dc[2]], dh[dc[3]], board, NF, FL)
    wins = (1 if p_he > d_he else 0) + (1 if p_om > d_om else 0)
    return 1 if wins == 2 else (0 if wins == 1 else -1)


@njit(cache=True)
def ev_preflop(ph, pp, d_rule, d_w, rollouts, HEW, HET, OMW, OMT, NF, FL):
    deck = np.empty(46, np.int64)
    j = 0
    for c in range(52):
        hit = False
        for k in range(6):
            if ph[k] == c:
                hit = True
        if not hit:
            deck[j] = c
            j += 1
    dh = np.empty(6, np.int64)
    board = np.empty(5, np.int64)
    s = 0.0
    for _ in range(rollouts):
        for k in range(11):
            r = k + np.random.randint(46 - k)
            deck[k], deck[r] = deck[r], deck[k]
        for k in range(6):
            dh[k] = deck[k]
        for k in range(5):
            board[k] = deck[6 + k]
        dp = choose_split(dh, d_rule, d_w, True, HEW, HET, OMW, OMT)
        s += _outcome(ph, pp, dh, dp, board, NF, FL)
    return s / rollouts


@njit(cache=True)
def ev_river(ph, pp, board, d_rule, d_w, rollouts, HEW, HET, OMW, OMT, NF, FL):
    deck = np.empty(41, np.int64)
    j = 0
    for c in range(52):
        hit = False
        for k in range(6):
            if ph[k] == c:
                hit = True
        for k in range(5):
            if board[k] == c:
                hit = True
        if not hit:
            deck[j] = c
            j += 1
    dh = np.empty(6, np.int64)
    s = 0.0
    for _ in range(rollouts):
        for k in range(6):
            r = k + np.random.randint(41 - k)
            deck[k], deck[r] = deck[r], deck[k]
        for k in range(6):
            dh[k] = deck[k]
        dp = choose_split(dh, d_rule, d_w, True, HEW, HET, OMW, OMT)
        s += _outcome(ph, pp, dh, dp, board, NF, FL)
    return s / rollouts


@njit(parallel=True, cache=True)
def simulate_s1(n, seed, d_rule, d_w, p_rule, p_w, pre_rollouts, river_rollouts, mc_seed,
                HEW, HET, OMW, OMT, NF, FL):
    ev_pre = np.zeros(n)
    ev_riv = np.zeros(n)
    outcome = np.zeros(n, np.int8)
    for i in prange(n):
        np.random.seed(seed + i)
        deck = np.arange(52)
        for k in range(17):
            r = k + np.random.randint(52 - k)
            deck[k], deck[r] = deck[r], deck[k]
        ph = deck[0:6].copy()
        dh = deck[6:12].copy()
        board = deck[12:17].copy()
        pp = choose_split(ph, p_rule, p_w, False, HEW, HET, OMW, OMT)
        dp = choose_split(dh, d_rule, d_w, True, HEW, HET, OMW, OMT)
        outcome[i] = _outcome(ph, pp, dh, dp, board, NF, FL)
        np.random.seed(mc_seed + i)
        ev_pre[i] = ev_preflop(ph, pp, d_rule, d_w, pre_rollouts, HEW, HET, OMW, OMT, NF, FL)
        ev_riv[i] = ev_river(ph, pp, board, d_rule, d_w, river_rollouts, HEW, HET, OMW, OMT, NF, FL)
    return ev_pre, ev_riv, outcome


def evaluate_s1(ev_pre, ev_riv, outcome, threshold):
    """Per-hand net result (in Base units) and total stake under strategy S1."""
    o = outcome.astype(np.float64)
    raise4 = ev_pre > threshold
    call = (~raise4) & (ev_riv > -0.5)
    fold = (~raise4) & (~call)
    result = np.where(raise4, 5 * o, np.where(call, 2 * o, -1.0))
    stake = np.where(raise4, 5.0, np.where(call, 2.0, 1.0))
    n = len(o)
    return {
        "threshold": float(threshold),
        "house_edge": float(-result.mean()), "house_edge_ci95": float(1.96 * result.std() / np.sqrt(n)),
        "element_of_risk": float(-result.mean() / stake.mean()), "avg_stake": float(stake.mean()),
        "raise4_rate": float(raise4.mean()), "call1_rate": float(call.mean()), "fold_rate": float(fold.mean()),
        "win": float((outcome == 1).mean()), "push": float((outcome == 0).mean()), "loss_at_showdown": float((outcome == -1).mean()),
        "result_sd": float(result.std()),
    }
