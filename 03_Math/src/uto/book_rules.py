"""The strategy book's decision rules (preflop / flop), as code. See the strategy book doc."""
import numpy as np
from .features import split_features


def preflop_raise(h, split):
    """Raise 4x preflop with a Hold'em pair of Jacks or better; Tens if 2+ Omaha cards are Ten or
    higher; Nines if 3+; Ace-King if 2+ Omaha cards are Ten or higher. Otherwise check."""
    f = split_features(np.asarray(h), split)
    if f["he_pair"]:
        return f["he_hi"] >= 9 or (f["he_hi"] == 8 and f["om_high"] >= 2) or (f["he_hi"] == 7 and f["om_high"] >= 3)
    return f["he_hi"] == 12 and f["he_lo"] == 11 and f["om_high"] >= 2
