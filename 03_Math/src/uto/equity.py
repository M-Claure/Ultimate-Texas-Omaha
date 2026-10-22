"""Starting-hand equity tables (vs. one random opponent hand of the same type, random board).

he_win[i], he_tie[i]: Hold'em 2-card hand, indexed by idx2(c0, c1) over all 1326 combos.
om_win[i], om_tie[i]: Omaha 4-card hand, indexed by idx4(...) over all 270,725 combos.
Computed by Monte Carlo once per suit-isomorphism class, then copied to every member.
"""
import os
import numpy as np
from numba import njit, prange
from .evaluator import tables, holdem_fast, omaha_fast

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


@njit(cache=True, inline="always")
def idx2(a, b):
    if a > b:
        a, b = b, a
    return a + b * (b - 1) // 2


@njit(cache=True, inline="always")
def _c(n, k):
    # small binomial for combinadic indexing
    if n < k:
        return 0
    r = 1
    for i in range(k):
        r = r * (n - i) // (i + 1)
    return r


@njit(cache=True)
def idx4(a, b, c, d):
    # sort ascending
    if a > b: a, b = b, a
    if c > d: c, d = d, c
    if a > c: a, c = c, a
    if b > d: b, d = d, b
    if b > c: b, c = c, b
    return a + _c(b, 2) + _c(c, 3) + _c(d, 4)


def _all_combos(k):
    from itertools import combinations
    return np.array(list(combinations(range(52), k)), np.int64)


def _canonical_keys(combos):
    """Suit-isomorphism class key for each combo (min over the 24 suit relabelings)."""
    from itertools import permutations
    ranks = combos >> 2
    suits = combos & 3
    best = None
    for perm in permutations(range(4)):
        p = np.array(perm)
        mapped = np.sort(ranks * 4 + p[suits], axis=1)
        key = np.zeros(len(combos), np.int64)
        for j in range(mapped.shape[1]):
            key = key * 52 + mapped[:, j]
        best = key if best is None else np.minimum(best, key)
    return best


@njit(parallel=True, cache=True)
def _mc_holdem(reps, trials, seed, NF, FL):
    n = reps.shape[0]
    win = np.zeros(n)
    tie = np.zeros(n)
    for i in prange(n):
        np.random.seed(seed + i)
        a = reps[i, 0]
        b = reps[i, 1]
        deck = np.empty(50, np.int64)
        j = 0
        for c in range(52):
            if c != a and c != b:
                deck[j] = c
                j += 1
        w = 0
        t = 0
        board = np.empty(5, np.int64)
        for _ in range(trials):
            # partial Fisher-Yates for 7 cards
            for k in range(7):
                r = k + np.random.randint(50 - k)
                deck[k], deck[r] = deck[r], deck[k]
            for k in range(5):
                board[k] = deck[2 + k]
            v1 = holdem_fast(a, b, board, NF, FL)
            v2 = holdem_fast(deck[0], deck[1], board, NF, FL)
            if v1 > v2:
                w += 1
            elif v1 == v2:
                t += 1
        win[i] = w / trials
        tie[i] = t / trials
    return win, tie


@njit(parallel=True, cache=True)
def _mc_omaha(reps, trials, seed, NF, FL):
    n = reps.shape[0]
    win = np.zeros(n)
    tie = np.zeros(n)
    for i in prange(n):
        np.random.seed(seed + i)
        deck = np.empty(48, np.int64)
        j = 0
        for c in range(52):
            if c != reps[i, 0] and c != reps[i, 1] and c != reps[i, 2] and c != reps[i, 3]:
                deck[j] = c
                j += 1
        w = 0
        t = 0
        board = np.empty(5, np.int64)
        for _ in range(trials):
            for k in range(9):
                r = k + np.random.randint(48 - k)
                deck[k], deck[r] = deck[r], deck[k]
            for k in range(5):
                board[k] = deck[4 + k]
            v1 = omaha_fast(reps[i, 0], reps[i, 1], reps[i, 2], reps[i, 3], board, NF, FL)
            v2 = omaha_fast(deck[0], deck[1], deck[2], deck[3], board, NF, FL)
            if v1 > v2:
                w += 1
            elif v1 == v2:
                t += 1
        win[i] = w / trials
        tie[i] = t / trials
    return win, tie


def build(he_trials=400_000, om_trials=4_000, seed=20261021, verbose=True):
    NF, FL = tables()
    out = {}
    for k, trials, fn, name in [(2, he_trials, _mc_holdem, "he"), (4, om_trials, _mc_omaha, "om")]:
        combos = _all_combos(k)
        keys = _canonical_keys(combos)
        uniq, first, inv = np.unique(keys, return_index=True, return_inverse=True)
        reps = combos[first]
        if verbose:
            print(f"{name}: {len(combos)} combos, {len(uniq)} classes, {trials} trials each")
        w, t = fn(reps, trials, seed, NF, FL)
        # scatter into combinadic-indexed arrays (idx2 / idx4 order)
        pos = np.array([idx2(*c) if k == 2 else idx4(*c) for c in combos], np.int64)
        W = np.zeros(len(combos), np.float32)
        T = np.zeros(len(combos), np.float32)
        W[pos] = w[inv]
        T[pos] = t[inv]
        out[name + "_win"] = W
        out[name + "_tie"] = T
        out[name + "_classes"] = np.int64(len(uniq))
    out["he_trials"] = np.int64(he_trials)
    out["om_trials"] = np.int64(om_trials)
    out["seed"] = np.int64(seed)
    return out


def load(path=None):
    path = path or os.path.join(DATA_DIR, "equity_tables.npz")
    d = np.load(path)
    return {k: d[k] for k in d.files}
