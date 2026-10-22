"""Hand-splitting rules (for the dealer house way and for reference players).

A split of 6 cards is identified by which pair (index 0..14 into PAIRS6) goes to Hold'em;
the other four cards (COMP6[p]) go to Omaha.

Rule codes
----------
RANDOM          uniformly random split (baseline: how much does a house way matter?)
HOLDEM_FIRST    Rules v0.1 house way (option A): best 2-card Hold'em by
                pair > suited > offsuit, then top rank, second rank, then suit tie-break
OMAHA_FIRST     option B: the 4 cards with the highest Omaha equity go to Omaha
WEIGHTED        option C: maximise  holdem_equity + w * omaha_equity
ORACLE          option D: Monte Carlo best response (see oracle_split), dealer only

"Equity" = probability of beating one random hand of the same type on a random board.
For the dealer, ties count in its favour (tie = player loses that hand), so the dealer
uses win+tie; players use win only.
"""
import numpy as np
from numba import njit
from .equity import idx2, idx4
from .evaluator import holdem_fast, omaha_pair

RANDOM, HOLDEM_FIRST, OMAHA_FIRST, WEIGHTED, ORACLE = 0, 1, 2, 3, 4
RULE_NAMES = {RANDOM: "Random", HOLDEM_FIRST: "A Hold'em-first (v0.1)",
              OMAHA_FIRST: "B Omaha-first", WEIGHTED: "C Weighted", ORACLE: "D Oracle"}

_p = []
for i in range(6):
    for j in range(i + 1, 6):
        _p.append((i, j))
PAIRS6 = np.array(_p, np.int64)                                     # 15 x 2
COMP6 = np.array([[k for k in range(6) if k not in pr] for pr in _p], np.int64)  # 15 x 4
# for each split p, the 6 pair-indices (into PAIRS6) that live inside its Omaha 4 cards
_pair_id = {pr: n for n, pr in enumerate(_p)}
COMP_PAIRS = np.array([[_pair_id[(c[a], c[b])] for a in range(4) for b in range(a + 1, 4)]
                       for c in COMP6.tolist()], np.int64)          # 15 x 6


@njit(cache=True)
def holdem_first_key(a, b):
    """Rules v0.1 ordering key for a 2-card Hold'em selection (bigger = preferred)."""
    if a < b:
        a, b = b, a            # a = higher card index (rank-major, suit order c<d<h<s)
    ra = a >> 2
    rb = b >> 2
    if ra == rb:
        cat = 2
    elif (a & 3) == (b & 3):
        cat = 1
    else:
        cat = 0
    return (cat << 24) | (ra << 20) | (rb << 16) | (a << 8) | b


@njit(cache=True)
def split_scores(h6, rule, w, ties, HEW, HET, OMW, OMT):
    """Score of each of the 15 splits under a heuristic rule (higher = chosen)."""
    s = np.zeros(15)
    for p in range(15):
        a = h6[PAIRS6[p, 0]]
        b = h6[PAIRS6[p, 1]]
        c = COMP6[p]
        i2 = idx2(a, b)
        i4 = idx4(h6[c[0]], h6[c[1]], h6[c[2]], h6[c[3]])
        he = HEW[i2] + (HET[i2] if ties else 0.0)
        om = OMW[i4] + (OMT[i4] if ties else 0.0)
        if rule == HOLDEM_FIRST:
            s[p] = holdem_first_key(a, b)
        elif rule == OMAHA_FIRST:
            s[p] = om + 1e-6 * he          # Omaha first, Hold'em equity as tie-break
        else:  # WEIGHTED
            s[p] = he + w * om
    return s


@njit(cache=True)
def choose_split(h6, rule, w, ties, HEW, HET, OMW, OMT):
    if rule == RANDOM:
        return np.random.randint(15)
    s = split_scores(h6, rule, w, ties, HEW, HET, OMW, OMT)
    best = 0
    for p in range(1, 15):
        if s[p] > s[best]:
            best = p
    return best


@njit(cache=True)
def oracle_split(h6, rollouts, player_rule, player_w, HEW, HET, OMW, OMT, NF, FL):
    """Option D: estimate the dealer's flat-bet result for each of its 15 splits by Monte Carlo
    against a reference player (who splits with player_rule) and pick the best.

    Dealer result per rollout: +1 player wins neither hand, -1 player wins both, 0 push.
    The same rollouts are used for all 15 splits (common random numbers).
    Caller must seed numba's RNG.
    """
    deck = np.empty(46, np.int64)
    j = 0
    for c in range(52):
        hit = False
        for k in range(6):
            if h6[k] == c:
                hit = True
        if not hit:
            deck[j] = c
            j += 1
    score = np.zeros(15)
    ph6 = np.empty(6, np.int64)
    board = np.empty(5, np.int64)
    hv = np.empty(15, np.int64)
    ov = np.empty(15, np.int64)
    for _ in range(rollouts):
        for k in range(11):
            r = k + np.random.randint(46 - k)
            deck[k], deck[r] = deck[r], deck[k]
        for k in range(6):
            ph6[k] = deck[k]
        for k in range(5):
            board[k] = deck[6 + k]
        pp = choose_split(ph6, player_rule, player_w, False, HEW, HET, OMW, OMT)
        pc = COMP6[pp]
        p_he = holdem_fast(ph6[PAIRS6[pp, 0]], ph6[PAIRS6[pp, 1]], board, NF, FL)
        p_om = 0
        for a in range(4):
            for b in range(a + 1, 4):
                v = omaha_pair(ph6[pc[a]], ph6[pc[b]], board, NF, FL)
                if v > p_om:
                    p_om = v
        for q in range(15):
            x = h6[PAIRS6[q, 0]]
            y = h6[PAIRS6[q, 1]]
            hv[q] = holdem_fast(x, y, board, NF, FL)
            ov[q] = omaha_pair(x, y, board, NF, FL)
        for q in range(15):
            d_om = 0
            for m in range(6):
                v = ov[COMP_PAIRS[q, m]]
                if v > d_om:
                    d_om = v
            wins = (1 if p_he > hv[q] else 0) + (1 if p_om > d_om else 0)
            if wins == 0:
                score[q] += 1.0
            elif wins == 2:
                score[q] -= 1.0
    return score / rollouts
