"""Flop decision data: random hands that the book CHECKS preflop (book split B1, preflop rule R2),
a random flop each, and P(win both)/P(lose both) given the flop (300 boards x 4 dealer hands)."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import numpy as np
from uto.equity import load
from uto.evaluator import tables
from uto.book_data import flop_given
from uto.house_way import SIMPLE, simple_code
from uto.player_split import book_split
from uto.book_rules import preflop_raise
T = load(); NF, FL = tables(); args = (T["he_win"], T["he_tie"], T["om_win"], T["om_tie"], NF, FL)
N = int(sys.argv[1]); rng = np.random.default_rng(53_000_000)
hands, splits = [], []
while len(hands) < N:
    h = rng.choice(52, 6, replace=False).astype(np.int64); p = book_split(h)
    if not preflop_raise(h, p):
        hands.append(h); splits.append(p)
t = time.time()
FLOP, EJ = flop_given(np.array(hands), np.array(splits, np.int64), 54_000_000, 300, 4, SIMPLE, simple_code(P=7, q=9, s=2), *args)
np.savez_compressed(os.path.join(HERE, "flop_data_b2.npz"), hands=np.array(hands), splits=np.array(splits), flop=FLOP, ej=EJ)
print("done", N, round(time.time() - t), "s")
