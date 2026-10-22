"""Player decision information at every betting point, independent of the paytable.

simulate_info stores, for each hand, Monte Carlo estimates of P(player wins overall) and
P(player loses overall) as seen by the player at three points:
  preflop (knows own 6 cards), flop (+3 board cards), river (+5 board cards)
plus the actual outcome. Because these are probabilities (not EVs), any payout / raise structure
can then be evaluated afterwards on the same hands (see evaluate_structure).

The player's policy in evaluate_structure is a threshold policy (raise preflop if the estimated
EV of raising beats a threshold, else raise on the flop if above another threshold, else call
or fold at the river by exact EV comparison). Thresholds are grid-searched for the player.
Not fully optimal -> house edges reported are upper bounds (truth is a bit lower).
"""
import numpy as np
from numba import njit, prange
from .house_way import choose_split
from .strategy import _outcome


@njit(cache=False)
def _mc(ph, pp, board, nboard, d_rule, d_w, rollouts, HEW, HET, OMW, OMT, NF, FL):
    """P(win), P(loss) given player's 6 cards + first nboard board cards."""
    excl = np.zeros(52, np.bool_)
    for k in range(6):
        excl[ph[k]] = True
    for k in range(nboard):
        excl[board[k]] = True
    m = 52 - 6 - nboard
    deck = np.empty(m, np.int64)
    j = 0
    for c in range(52):
        if not excl[c]:
            deck[j] = c
            j += 1
    need = 6 + (5 - nboard)
    dh = np.empty(6, np.int64)
    bd = np.empty(5, np.int64)
    for k in range(nboard):
        bd[k] = board[k]
    w = 0
    l = 0
    for _ in range(rollouts):
        for k in range(need):
            r = k + np.random.randint(m - k)
            deck[k], deck[r] = deck[r], deck[k]
        for k in range(6):
            dh[k] = deck[k]
        for k in range(nboard, 5):
            bd[k] = deck[6 + k - nboard]
        dp = choose_split(dh, d_rule, d_w, True, HEW, HET, OMW, OMT)
        o = _outcome(ph, pp, dh, dp, bd, NF, FL)
        if o == 1:
            w += 1
        elif o == -1:
            l += 1
    return w / rollouts, l / rollouts


@njit(parallel=True)
def simulate_info(n, seed, d_rule, d_w, p_rule, p_w, rollouts, mc_seed,
                  HEW, HET, OMW, OMT, NF, FL):
    info = np.zeros((n, 6), np.float32)   # pre_w, pre_l, flop_w, flop_l, riv_w, riv_l
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
        a, b = _mc(ph, pp, board, 0, d_rule, d_w, rollouts[0], HEW, HET, OMW, OMT, NF, FL)
        info[i, 0] = a
        info[i, 1] = b
        a, b = _mc(ph, pp, board, 3, d_rule, d_w, rollouts[1], HEW, HET, OMW, OMT, NF, FL)
        info[i, 2] = a
        info[i, 3] = b
        a, b = _mc(ph, pp, board, 5, d_rule, d_w, rollouts[2], HEW, HET, OMW, OMT, NF, FL)
        info[i, 4] = a
        info[i, 5] = b
    return info, outcome


def evaluate_structure(info, outcome, pre=4, flop=2, river=1, base_win=1.0, river_fold=True,
                       t_pre=0.0, t_flop=0.0):
    """Net result per hand (Base units) for one payout/raise structure and player thresholds.

    pre/flop/river: raise multiples (0 = no raise allowed at that point)
    base_win: what the Base pays on an overall win (1.0 = even money, 0 = push)
    Play bet always pays 1:1 on win, pushes on push, loses on loss. Base loses on loss, pushes on push.
    Threshold rule: raise at a point if the estimated per-unit edge of the raise (P(win)-P(loss))
    exceeds the threshold.
    """
    o = outcome.astype(np.float64)
    pw, pl = info[:, 0], info[:, 1]
    fw, fl = info[:, 2], info[:, 3]
    rw, rl = info[:, 4], info[:, 5]
    base = np.where(o == 1, base_win, np.where(o == -1, -1.0, 0.0))
    r_pre = (pre > 0) & ((pw - pl) > t_pre)
    r_flop = (~r_pre) & (flop > 0) & ((fw - fl) > t_flop)
    rest = ~(r_pre | r_flop)
    # river: call if EV(call) > EV(fold) = -1  (EV(call) = river*(w-l) + base_win*w - l)
    if river > 0:
        call_ev = river * (rw - rl) + base_win * rw - rl
        call = rest & ((call_ev > -1.0) if river_fold else np.ones(len(o), bool))
    else:
        call = rest & np.ones(len(o), bool)
    fold = rest & ~call
    play = np.where(r_pre, pre, np.where(r_flop, flop, np.where(call, river, 0.0)))
    result = np.where(fold, -1.0, base + play * o)
    stake = np.where(fold, 1.0, 1.0 + play)
    n = len(o)
    return {
        "house_edge": float(-result.mean()), "ci95": float(1.96 * result.std() / np.sqrt(n)),
        "element_of_risk": float(-result.mean() / stake.mean()), "avg_total_bet": float(stake.mean()),
        "raise_pre": float(r_pre.mean()), "raise_flop": float(r_flop.mean()),
        "call_river": float(call.mean()), "fold": float(fold.mean()),
        "player_win_rate": float(((o == 1) & ~fold).mean()),
        "push_rate": float(((o == 0) & ~fold).mean()),
        "player_net_positive_rate": float((result > 0).mean()),
    }


def best_player_response(info, outcome, grid_pre=None, grid_flop=None, **structure):
    """Grid-search player thresholds; return the result with the LOWEST house edge."""
    grid_pre = grid_pre if grid_pre is not None else np.arange(-0.05, 0.41, 0.025)
    grid_flop = grid_flop if grid_flop is not None else np.arange(-0.2, 0.41, 0.05)
    best = None
    for a in grid_pre:
        for b in grid_flop:
            r = evaluate_structure(info, outcome, t_pre=a, t_flop=b, **structure)
            if best is None or r["house_edge"] < best["house_edge"]:
                best = dict(r, t_pre=float(a), t_flop=float(b))
    return best
