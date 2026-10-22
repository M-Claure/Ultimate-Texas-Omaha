"""Rebuild data/equity_tables.npz (about 1-2 minutes on 2 cores). Run from 03_Math/."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from uto.equity import build, DATA_DIR

t = time.time()
out = build()  # defaults: 400k Hold'em trials/class, 4k Omaha trials/class, seed 20261021
os.makedirs(DATA_DIR, exist_ok=True)
np.savez_compressed(os.path.join(DATA_DIR, "equity_tables.npz"), **out)
print(f"done in {time.time() - t:.0f}s")
