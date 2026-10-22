"""Human-readable hand features used to express the strategy book."""
import numpy as np
from .evaluator import eval_cards, category
from .house_way import PAIRS6, COMP6

R = "23456789TJQKA"


def he_features(c1, c2):
    r1, r2 = sorted([c1 >> 2, c2 >> 2], reverse=True)
    return dict(he_pair=int(r1 == r2), he_hi=r1, he_lo=r2, he_suited=int((c1 & 3) == (c2 & 3)), he_gap=r1 - r2)


def om_features(cs):
    rs = sorted([c >> 2 for c in cs], reverse=True)
    ss = [c & 3 for c in cs]
    cnt = np.bincount(rs, minlength=13)
    pairs = [r for r in range(13) if cnt[r] >= 2]
    sc = sorted(np.bincount(ss, minlength=4), reverse=True)
    uniq = sorted(set(rs))
    # connectedness: largest number of distinct ranks inside any 5-rank window (A counts low too)
    rr = set(uniq) | ({-1} if 12 in uniq else set())
    conn = max(sum(1 for x in range(lo, lo + 5) if x in rr) for lo in range(-1, 9))
    return dict(om_pairs=len(pairs), om_pair_hi=max(pairs) if pairs else -1,
                om_ds=int(sc[0] == 2 and sc[1] == 2), om_suited=int(sc[0] >= 2),
                om_high=sum(1 for r in rs if r >= 8), om_ace=int(12 in rs), om_top=rs[0], om_conn=conn,
                om_trips=int(cnt.max() >= 3))


def split_features(hand, split):
    a, b = hand[PAIRS6[split]]
    f = he_features(int(a), int(b))
    f.update(om_features([int(x) for x in hand[COMP6[split]]]))
    return f


def _cat5(cs):
    return category(eval_cards(np.array(cs, np.int64), 5))


def flop_features(hand, split, flop):
    """Player's made hands / draws on the flop (Hold'em: 2 hole + 3 flop; Omaha: exactly 2 + 3)."""
    he = [int(x) for x in hand[PAIRS6[split]]]
    om = [int(x) for x in hand[COMP6[split]]]
    fl = [int(x) for x in flop]
    fr = sorted([c >> 2 for c in fl], reverse=True)
    he_cat = _cat5(he + fl)
    board_cat = 1 if len(set(fr)) < 3 else 0
    hr = sorted([c >> 2 for c in he], reverse=True)
    he_pair_hole = he_cat >= 1 and (hr[0] in fr or hr[1] in fr or hr[0] == hr[1])
    top_pair_plus = he_cat >= 2 or (he_cat == 1 and (hr[0] == hr[1] and hr[0] > fr[0] or fr[0] in hr))
    # Hold'em flush draw: 4 cards of a suit among 5, using at least one hole card
    def fd(cards_hole, cards_board, need_hole):
        best = 0
        for s in range(4):
            nh = sum(1 for c in cards_hole if c & 3 == s)
            nb = sum(1 for c in cards_board if c & 3 == s)
            if nh >= need_hole:
                best = max(best, min(nh, 2 if need_hole == 2 else nh) + nb)
        return best
    he_fd = int(he_cat < 5 and fd(he, fl, 1) >= 4)
    # Omaha
    best = 0
    for i in range(4):
        for j in range(i + 1, 4):
            best = max(best, _cat5([om[i], om[j]] + fl))
    om_cat = best
    om_fd = 0
    for s in range(4):
        if sum(1 for c in om if c & 3 == s) >= 2 and sum(1 for c in fl if c & 3 == s) == 2:
            om_fd = 1
    om_ranks = sorted([c >> 2 for c in om], reverse=True)
    om_overpair = int(any(om_ranks.count(r) >= 2 and r > fr[0] for r in set(om_ranks)))
    om_top_pair = int(any(r == fr[0] for r in om_ranks))
    return dict(he_cat=he_cat, he_top_pair_plus=int(top_pair_plus), he_pair_hole=int(he_pair_hole), he_fd=he_fd,
                om_cat=om_cat, om_fd=om_fd, om_overpair=om_overpair, om_top_pair=om_top_pair,
                board_paired=board_cat, board_high=fr[0], he_hi=hr[0], he_pocket=int(hr[0] == hr[1]))
