"""Player split rules for the strategy book (pure Python; used for analysis and the book)."""
import numpy as np
from .house_way import PAIRS6, COMP6

_PIDX = {tuple(p): i for i, p in enumerate(PAIRS6.tolist())}


def _pick(h, idxs):
    return _PIDX[tuple(sorted(idxs))]


def _suit_tiebreak(h, cands):
    """Among candidate splits, keep the most same-suited cards together in Omaha, then
    the higher suits in Hold'em (spades high)."""
    best, bk = None, None
    for s in cands:
        om = h[COMP6[s]] & 3
        sc = np.bincount(om, minlength=4)
        a, b = sorted(h[PAIRS6[s]], reverse=True)
        key = (int((sc >= 2).sum()), int(a), int(b))
        if bk is None or key > bk:
            best, bk = s, key
    return best


def book_split(h, variant="B1"):
    """Variant "B1" (strategy book, see EXP-004): rules 1-2 below, then
      3. One pair: the pair in Hold'em, unless the pair is Tens or lower and you also hold an
         unpaired Ace AND King: then Ace-King goes in Hold'em.
      4. No pair: (a) second-highest card Queen or higher -> two highest cards in Hold'em;
         (b) otherwise, holding an Ace -> the Ace with the lowest card of its suit (no suited
         card: Ace with your lowest card); (c) otherwise -> your two lowest cards in Hold'em.
    Variant "P1" (earlier draft):
      1. Three or four of a kind: two of them in Hold'em.
      2. Two or three pairs: the highest pair in Hold'em.
      3. One pair: the pair in Hold'em (any rank).
      4. No pair: if your highest card and your lowest card are the same suit, put those two in
         Hold'em; otherwise put your two highest cards in Hold'em.
      5. Suits: keep same-suited cards together in Omaha.
    """
    h = np.asarray(h)
    r = h >> 2
    cnt = np.bincount(r, minlength=13)
    def ranks_split(ra, rb):
        c = [s for s in range(15) if sorted(r[PAIRS6[s]].tolist()) == sorted([ra, rb])]
        return _suit_tiebreak(h, c)
    big = [x for x in range(13) if cnt[x] >= 3]
    if big:
        x = max(big)
        return ranks_split(x, x)
    pairs = sorted([x for x in range(13) if cnt[x] == 2], reverse=True)
    if len(pairs) >= 2:
        x = pairs[0] if variant != "lowpair" else pairs[-1]
        return ranks_split(x, x)
    order = sorted(range(6), key=lambda k: (-r[k], -h[k]))
    if len(pairs) == 1:
        if variant == "B1" and pairs[0] <= 8 and cnt[12] == 1 and cnt[11] == 1:
            return ranks_split(12, 11)
        return ranks_split(pairs[0], pairs[0])
    if variant == "B1":
        if r[order[1]] >= 10:
            return ranks_split(r[order[0]], r[order[1]])
        if r[order[0]] == 12:
            ace = order[0]
            same = [k for k in order[1:] if (h[k] & 3) == (h[ace] & 3)]
            return _pick(h, [ace, same[-1] if same else order[-1]])
        return _pick(h, [order[4], order[5]])
    top, low = order[0], order[-1]
    if (h[top] & 3) == (h[low] & 3):
        return _pick(h, [top, low])
    return ranks_split(r[order[0]], r[order[1]])
