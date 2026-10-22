import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from uto.cards import cards
from uto.house_way import choose_split, PAIRS6, HOLDEM_FIRST, WEIGHTED, OMAHA_FIRST
from uto.equity import load

T = load(); A = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"])

def he_cards(hand, rule, w=1.0, ties=True):
    h = np.array(cards(hand), np.int64)
    p = choose_split(h, rule, w, ties, *A)
    return sorted(cards(hand).index(int(h[i])) for i in PAIRS6[p])

def test_rule_a_prefers_pair():
    # pair of 7s beats suited A-K for Hold'em under v0.1 house way
    assert he_cards("7c 7d As Ks 2h 3c", HOLDEM_FIRST) == [0, 1]

def test_rule_a_higher_pair_and_suited():
    assert he_cards("7c 7d Qc Qd 2h 3c", HOLDEM_FIRST) == [2, 3]
    assert he_cards("Ah Kh Qs Jd 2c 3d", HOLDEM_FIRST) == [0, 1]   # suited AK over offsuit AQ
    assert he_cards("Ah Kh As Qd 2c 3d", HOLDEM_FIRST) == [0, 2]   # pair of aces wins

def test_rule_a_suit_tiebreak():
    # two identical-rank suited options: spades beat hearts
    assert he_cards("Ah Kh As Ks 2c 3d", HOLDEM_FIRST) in ([0, 2], [1, 3], [2, 3])
    # pairs: AA available -> AsAh (highest suits)
    assert he_cards("Ac Ad Ah As 2c 3d", HOLDEM_FIRST) == [2, 3]

def test_weighted_is_sane():
    # AA to Hold'em is not forced, but split must be one of 15 and keep 4 for Omaha
    hand = "Ac Ad Kc Kd 7h 2s"
    assert len(he_cards(hand, WEIGHTED, 0.5)) == 2


def test_house_way_H():
    from uto.house_way import SIMPLE, simple_code
    H = simple_code(P=7, q=9, s=2)
    assert he_cards("5c 5d As Kh 9c 2d", SIMPLE, H) == [2, 3]   # small pair, A & K both J+ -> AK
    assert he_cards("5c 5d As Th 9c 2d", SIMPLE, H) == [0, 1]   # T is below J -> keep the pair
    assert he_cards("9c 9d As Kh 7c 2d", SIMPLE, H) == [0, 1]   # 9s or better -> pair
    assert he_cards("9c 9d 4s 4h Ac 2d", SIMPLE, H) == [0, 1]   # two pairs -> higher pair
    assert he_cards("Ac Jd 9s 7h 4c 2d", SIMPLE, H) == [0, 1]   # no pair -> two highest
    assert he_cards("7c 7d 7s Kh 4c 2d", SIMPLE, H)[0] < 3      # trips -> two of the trips
    # suit choice: Hold'em takes the 7 whose removal keeps Omaha suited
    hand = "7c 7d 7s Kc 4d 2h"   # leaving 7c with Kc and 7d with 4d keeps Omaha double-suited
    assert he_cards(hand, SIMPLE, H) == [0, 2] or he_cards(hand, SIMPLE, H) == [1, 2]
