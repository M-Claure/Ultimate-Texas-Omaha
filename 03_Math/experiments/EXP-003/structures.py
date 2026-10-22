import numpy as np
# [R1 preflop, R2 flop, R3 river, Base pays on win (bw), river fold allowed]
RAISES = [(4, 2, 1), (3, 2, 1), (3, 1, 1), (2, 1, 1)]
BW = [1.0, 0.5, 0.25, 0.0]
FOLD = [1, 0]
ST = np.array([[0, 0, 0, 1.0, 0]] + [[r[0], r[1], r[2], b, f] for r in RAISES for b in BW for f in FOLD], float)
def label(row):
    if row[0] == 0:
        return "flat Base only (check)"
    return f"{int(row[0])}x/{int(row[1])}x/{int(row[2])}x, Base on win {row[3]:g}, {'fold' if row[4] else 'no fold'}"
