"""Fast poker hand evaluators (numba).

Hand values are integers: larger = stronger, equal = exact tie.
value = category << 20 | k1 << 16 | k2 << 12 | k3 << 8 | k4 << 4 | k5
categories: 0 high card, 1 pair, 2 two pair, 3 trips, 4 straight,
            5 flush, 6 full house, 7 quads, 8 straight flush
"""
import numpy as np
from numba import njit

HIGH, PAIR, TWO_PAIR, TRIPS, STRAIGHT, FLUSH, FULL_HOUSE, QUADS, STRAIGHT_FLUSH = range(9)
CATEGORY_NAMES = ["High card", "Pair", "Two pair", "Trips", "Straight",
                  "Flush", "Full house", "Quads", "Straight flush"]


@njit(cache=True)
def _straight_high(mask):
    """Highest straight top rank in a 13-bit rank mask, or -1. Handles A-2-3-4-5."""
    for top in range(12, 3, -1):
        need = 0x1F << (top - 4)
        if (mask & need) == need:
            return top
    # wheel: A,2,3,4,5 -> top card is 5 (rank index 3)
    if (mask & 0x100F) == 0x100F:
        return 3
    return -1


@njit(cache=True)
def _pack(cat, a, b, c, d, e):
    return (cat << 20) | (a << 16) | (b << 12) | (c << 8) | (d << 4) | e


@njit(cache=True)
def eval_cards(cs, n):
    """Best 5-card hand value from the first n cards of array cs (5 <= n <= 7)."""
    cnt = np.zeros(13, np.int64)
    scnt = np.zeros(4, np.int64)
    smask = np.zeros(4, np.int64)
    mask = 0
    for i in range(n):
        r = cs[i] >> 2
        s = cs[i] & 3
        cnt[r] += 1
        scnt[s] += 1
        smask[s] |= 1 << r
        mask |= 1 << r
    # flush / straight flush
    fsuit = -1
    for s in range(4):
        if scnt[s] >= 5:
            fsuit = s
    if fsuit >= 0:
        sh = _straight_high(smask[fsuit])
        if sh >= 0:
            return _pack(STRAIGHT_FLUSH, sh, 0, 0, 0, 0)
    # quads / trips / pairs
    quad = -1
    trips1 = -1
    trips2 = -1
    pair1 = -1
    pair2 = -1
    pair3 = -1
    for r in range(12, -1, -1):
        c = cnt[r]
        if c == 4:
            quad = r
        elif c == 3:
            if trips1 < 0:
                trips1 = r
            elif trips2 < 0:
                trips2 = r
        elif c == 2:
            if pair1 < 0:
                pair1 = r
            elif pair2 < 0:
                pair2 = r
            elif pair3 < 0:
                pair3 = r
    if quad >= 0:
        k = -1
        for r in range(12, -1, -1):
            if r != quad and cnt[r] > 0:
                k = r
                break
        return _pack(QUADS, quad, k, 0, 0, 0)
    if trips1 >= 0:
        p = pair1
        if trips2 > p:
            p = trips2
        if p >= 0:
            return _pack(FULL_HOUSE, trips1, p, 0, 0, 0)
    if fsuit >= 0:
        ks = np.zeros(5, np.int64)
        j = 0
        for r in range(12, -1, -1):
            if (smask[fsuit] >> r) & 1:
                ks[j] = r
                j += 1
                if j == 5:
                    break
        return _pack(FLUSH, ks[0], ks[1], ks[2], ks[3], ks[4])
    sh = _straight_high(mask)
    if sh >= 0:
        return _pack(STRAIGHT, sh, 0, 0, 0, 0)
    ks = np.zeros(5, np.int64)
    if trips1 >= 0:
        j = 0
        for r in range(12, -1, -1):
            if r != trips1 and cnt[r] > 0:
                ks[j] = r
                j += 1
                if j == 2:
                    break
        return _pack(TRIPS, trips1, ks[0], ks[1], 0, 0)
    if pair2 >= 0:
        k = -1
        for r in range(12, -1, -1):
            if r != pair1 and r != pair2 and cnt[r] > 0:
                k = r
                break
        return _pack(TWO_PAIR, pair1, pair2, k, 0, 0)
    if pair1 >= 0:
        j = 0
        for r in range(12, -1, -1):
            if r != pair1 and cnt[r] > 0:
                ks[j] = r
                j += 1
                if j == 3:
                    break
        return _pack(PAIR, pair1, ks[0], ks[1], ks[2], 0)
    j = 0
    for r in range(12, -1, -1):
        if cnt[r] > 0:
            ks[j] = r
            j += 1
            if j == 5:
                break
    return _pack(HIGH, ks[0], ks[1], ks[2], ks[3], ks[4])


@njit(cache=True)
def eval_holdem(h0, h1, board):
    """Hold'em: best 5 of 2 hole + 5 board (any combination)."""
    cs = np.empty(7, np.int64)
    cs[0] = h0
    cs[1] = h1
    for i in range(5):
        cs[2 + i] = board[i]
    return eval_cards(cs, 7)


# the 10 ways to choose 3 of 5 board cards
BOARD3 = np.array([[0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 2, 3], [0, 2, 4],
                   [0, 3, 4], [1, 2, 3], [1, 2, 4], [1, 3, 4], [2, 3, 4]], np.int64)
# the 6 ways to choose 2 of 4 hole cards
HOLE2 = np.array([[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]], np.int64)


@njit(cache=True)
def eval_pair_board3(a, b, board):
    """Best value using exactly hole cards a,b and exactly 3 of the 5 board cards."""
    cs = np.empty(5, np.int64)
    best = -1
    cs[0] = a
    cs[1] = b
    for t in range(10):
        cs[2] = board[BOARD3[t, 0]]
        cs[3] = board[BOARD3[t, 1]]
        cs[4] = board[BOARD3[t, 2]]
        v = eval_cards(cs, 5)
        if v > best:
            best = v
    return best


@njit(cache=True)
def eval_omaha(hole4, board):
    """Omaha: exactly 2 of 4 hole cards + exactly 3 of 5 board cards."""
    best = -1
    for p in range(6):
        v = eval_pair_board3(hole4[HOLE2[p, 0]], hole4[HOLE2[p, 1]], board)
        if v > best:
            best = v
    return best


def category(value: int) -> int:
    return value >> 20


# ---------------------------------------------------------------------------
# Fast 5-card evaluation via lookup tables (used in the hot simulation loops).
# NF[sorted-rank index] = value for non-flush hands; FL[13-bit rank mask] = value for flushes.
# Tables are built from eval_cards, so they agree with it by construction (and tests check it).
# ---------------------------------------------------------------------------

@njit(cache=True)
def build_tables():
    nf = np.zeros(13 ** 5, np.int32)
    fl = np.zeros(1 << 13, np.int32)
    cs = np.empty(5, np.int64)
    for a in range(13):
        for b in range(a + 1):
            for c in range(b + 1):
                for d in range(c + 1):
                    for e in range(d + 1):
                        if a == e:          # five of a kind impossible
                            continue
                        # non-flush: give suits 0,1,2,3,0 (never 5 of a suit)
                        cs[0] = a * 4 + 0
                        cs[1] = b * 4 + 1
                        cs[2] = c * 4 + 2
                        cs[3] = d * 4 + 3
                        cs[4] = e * 4 + 0
                        idx = (((a * 13 + b) * 13 + c) * 13 + d) * 13 + e
                        nf[idx] = eval_cards(cs, 5)
                        if a > b and b > c and c > d and d > e:
                            for i in range(5):
                                cs[i] = (cs[i] >> 2) * 4  # all clubs
                            fl[(1 << a) | (1 << b) | (1 << c) | (1 << d) | (1 << e)] = eval_cards(cs, 5)
    return nf, fl


@njit(cache=True, inline="always")
def eval5(c0, c1, c2, c3, c4, NF, FL):
    s = c0 & 3
    if (c1 & 3) == s and (c2 & 3) == s and (c3 & 3) == s and (c4 & 3) == s:
        return FL[(1 << (c0 >> 2)) | (1 << (c1 >> 2)) | (1 << (c2 >> 2)) | (1 << (c3 >> 2)) | (1 << (c4 >> 2))]
    a = c0 >> 2
    b = c1 >> 2
    c = c2 >> 2
    d = c3 >> 2
    e = c4 >> 2
    # sorting network (descending) for 5 elements
    if a < b: a, b = b, a
    if d < e: d, e = e, d
    if c < e: c, e = e, c
    if c < d: c, d = d, c
    if b < e: b, e = e, b
    if a < d: a, d = d, a
    if a < c: a, c = c, a
    if b < d: b, d = d, b
    if b < c: b, c = c, b
    return NF[(((a * 13 + b) * 13 + c) * 13 + d) * 13 + e]


@njit(cache=True)
def omaha_pair(a, b, board, NF, FL):
    """Best value using exactly hole cards a,b + exactly 3 of 5 board cards (fast)."""
    best = 0
    for t in range(10):
        v = eval5(a, b, board[BOARD3[t, 0]], board[BOARD3[t, 1]], board[BOARD3[t, 2]], NF, FL)
        if v > best:
            best = v
    return best


@njit(cache=True)
def omaha_fast(h0, h1, h2, h3, board, NF, FL):
    best = omaha_pair(h0, h1, board, NF, FL)
    v = omaha_pair(h0, h2, board, NF, FL)
    if v > best: best = v
    v = omaha_pair(h0, h3, board, NF, FL)
    if v > best: best = v
    v = omaha_pair(h1, h2, board, NF, FL)
    if v > best: best = v
    v = omaha_pair(h1, h3, board, NF, FL)
    if v > best: best = v
    v = omaha_pair(h2, h3, board, NF, FL)
    if v > best: best = v
    return best


# the 21 ways to choose 5 of 7
_C75 = []
for _i in range(7):
    for _j in range(_i + 1, 7):
        _C75.append([k for k in range(7) if k != _i and k != _j])
C75 = np.array(_C75, np.int64)


@njit(cache=True)
def holdem_fast(h0, h1, board, NF, FL):
    """Hold'em best of 7 via 21 table lookups."""
    cs = np.empty(7, np.int64)
    cs[0] = h0
    cs[1] = h1
    for i in range(5):
        cs[2 + i] = board[i]
    best = 0
    for k in range(21):
        v = eval5(cs[C75[k, 0]], cs[C75[k, 1]], cs[C75[k, 2]], cs[C75[k, 3]], cs[C75[k, 4]], NF, FL)
        if v > best:
            best = v
    return best


_TABLES = None


def tables():
    """Return (NF, FL), building once per process."""
    global _TABLES
    if _TABLES is None:
        _TABLES = build_tables()
    return _TABLES
