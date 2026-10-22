import sys, os, itertools, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from uto.cards import cards
from uto.evaluator import eval_cards, eval_holdem, eval_omaha, category

def ev(s):
    c = np.array(cards(s), np.int64)
    return eval_cards(c, len(c))

def test_categories():
    assert category(ev("As Ks Qs Js Ts")) == 8
    assert category(ev("5d 4d 3d 2d Ad")) == 8          # steel wheel
    assert category(ev("9c 9d 9h 9s 2c")) == 7
    assert category(ev("9c 9d 9h 2s 2c")) == 6
    assert category(ev("Ah 9h 7h 4h 2h")) == 5
    assert category(ev("5c 4d 3h 2s Ad")) == 4          # wheel
    assert category(ev("Tc Jd Qh Ks Ad")) == 4
    assert category(ev("9c 9d 9h 3s 2c")) == 3
    assert category(ev("9c 9d 3h 3s 2c")) == 2
    assert category(ev("9c 9d 4h 3s 2c")) == 1
    assert category(ev("Kc 9d 4h 3s 2c")) == 0

def test_ordering():
    assert ev("5c 4d 3h 2s Ad") < ev("6c 5d 4h 3s 2d")   # wheel lowest straight
    assert ev("Ac Ad Kh Ks 2c") > ev("Ac Ad Qh Qs Kc")
    assert ev("Ac Ad Kh Ks 2c") < ev("Ac Ad Kh Ks 3c")   # kicker
    assert ev("Ah Kh 7h 4h 2h") == ev("As Ks 7s 4s 2s")  # exact tie

def test_seven_card():
    assert category(ev("Ah Kh Qh Jh Th 2c 2d")) == 8
    assert category(ev("Ah Ad Ac Kh Kd Kc 2s")) == 6        # two trips -> boat
    assert ev("Ah Ad Ac Kh Kd Kc 2s") == ev("Ah Ad Ac Kh Kd 3c 2s")
    assert category(ev("Ah Ad Kh Kd Qh Qd 2s")) == 2
    assert ev("Ah Ad Kh Kd Qh Qd 2s") == ev("Ah Ad Kh Kd Qh 3d 2s")  # third pair is kicker

def test_board_play_holdem():
    board = np.array(cards("As Ks Qs Js Ts"), np.int64)
    assert eval_holdem(0, 1, board) == eval_holdem(4, 5, board)  # both play the royal

def test_omaha_exactly_two():
    board = np.array(cards("As Ks Qs Js 2d"), np.int64)
    # one spade in hand: no flush in Omaha (needs 2 hole spades)
    h = np.array(cards("Ts 3c 4c 5d"), np.int64)
    assert category(eval_omaha(h, board)) < 5
    h2 = np.array(cards("Ts 9s 4c 5d"), np.int64)
    assert category(eval_omaha(h2, board)) == 8
    # four of a kind on board-ish: quads in hand cannot use 4 hole cards
    board2 = np.array(cards("Ac 7d 8h 2s 3c"), np.int64)
    h3 = np.array(cards("Ad Ah As Kc"), np.int64)
    assert category(eval_omaha(h3, board2)) == 3  # only trips (2 hole aces + board ace)

def test_vs_phevaluator():
    from phevaluator import evaluate_cards, evaluate_omaha_cards
    from uto.cards import name
    rng = random.Random(12345)
    for _ in range(20000):
        d = rng.sample(range(52), 18)
        a7, b7 = d[:7], d[7:14]
        va = eval_cards(np.array(a7, np.int64), 7); vb = eval_cards(np.array(b7, np.int64), 7)
        pa = evaluate_cards(*[name(c) for c in a7]); pb = evaluate_cards(*[name(c) for c in b7])
        # phevaluator: lower is better
        assert (va > vb) == (pa < pb) and (va == vb) == (pa == pb)
    for _ in range(20000):
        d = rng.sample(range(52), 13)
        board, h1, h2 = d[:5], d[5:9], d[9:13]
        v1 = eval_omaha(np.array(h1, np.int64), np.array(board, np.int64))
        v2 = eval_omaha(np.array(h2, np.int64), np.array(board, np.int64))
        p1 = evaluate_omaha_cards(*[name(c) for c in board], *[name(c) for c in h1])
        p2 = evaluate_omaha_cards(*[name(c) for c in board], *[name(c) for c in h2])
        assert (v1 > v2) == (p1 < p2) and (v1 == v2) == (p1 == p2)

def test_fast_matches_reference():
    from uto.evaluator import tables, eval5, holdem_fast, omaha_fast
    NF, FL = tables()
    rng = random.Random(7)
    for _ in range(30000):
        d = rng.sample(range(52), 11)
        board = np.array(d[:5], np.int64)
        assert eval5(*d[:5], NF, FL) == eval_cards(board, 5)
        assert holdem_fast(d[5], d[6], board, NF, FL) == eval_holdem(d[5], d[6], board)
        assert omaha_fast(d[7], d[8], d[9], d[10], board, NF, FL) == eval_omaha(np.array(d[7:11], np.int64), board)
