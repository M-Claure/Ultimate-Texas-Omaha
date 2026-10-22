# EXP-003 — House edge under optimal (perfect) player play

| Field | Value |
|---|---|
| Date | 2026-10-21 |
| Rules tested | v0.2 hand rules (6 cards, 2 Hold'em / 4 Omaha, tie = lost hand, 2 wins = WIN, 1 = PUSH, 0 = LOSS) with dealer **House Way H**, and 33 payout/raise structures |
| Code | `03_Math/src/uto/optimal2.py` (engine), `exact_check.py` (validation); scripts in this folder |
| Hands | 30,000 random player hands (seeds 31,000,000+), every structure solved on the same hands |
| Engine settings | per hand: 8,000 joint samples for linear terms; 24 flops × 8 turn/river boards × 160 dealer hands; 200 extra joint samples per flop |

## What "optimal play" means here
For every player hand the engine finds the best possible decisions, working backwards:
1. **River** (if no raise yet): call 1× or fold, whichever has the higher expected value.
2. **Flop** (if no raise yet): raise 2× or check, comparing raising now with the best river play later.
3. **Preflop**: raise 4× or check, comparing with the best flop/river play later.
4. **Split**: the one of 15 possible splits with the highest value under the play above.

The dealer always uses House Way H. Probabilities come from Monte Carlo over the unseen cards.

## How accurate it is
- **Exact check:** at the river, sampled win/loss probabilities match a full enumeration of all 4,496,388 possible dealer hands to within 0.2–0.5 percentage points (4 test boards).
- **Bracket:** each number is given as a range. The low end uses the same samples to make and score decisions, which slightly flatters the player. The high end makes each decision on one half of the samples and scores it on the other, which is a strategy a player could really follow, so it slightly understates the player. **The true optimal-play house edge lies inside the range.** The midpoint is reported.
- **Sampling error:** ±0.11–0.18% at 95% after a control variate (hand-strength features with exactly known averages; it removes ~92% of hand-to-hand variance).
- **Consistency checks:** optimal play beats every simpler strategy tested earlier. Flat-bet edge drops from 2.25% (heuristic split) to 1.22% (optimal split). Under v0.2 payouts the player's edge rises from 21.1% (threshold strategy, EXP-002) to 23.2%.

## Result for the candidate from EXP-002
**4×/2×/1×, river fold allowed, Base pushes when the player wins:**

| Measure | Value |
|---|---|
| House edge (per Base) | **+0.15%** (range −0.82% to +1.12%) |
| Element of risk | ≈ 0.05% |
| Average total bet | 2.94 Base units |
| Standard deviation | 1.93 |
| Preflop 4× raise | 28.3% of hands |
| Flop 2× raise | 23.5% of hands |
| River fold | 14.3% of hands |
| Player wins (both hands) | 23.3% |
| Player loses (incl. folds) | 29.3% |
| Push | 47.4% |

**Verdict: not high enough.** With perfect play the game is roughly break-even. The threshold player in EXP-002 had overstated the house edge by ~2%.

## All structures (house edge per Base under optimal play; midpoint and range)
| Raises | Base on win | River fold | House edge | Range | Element of risk | Avg bet | SD |
|---|---|---|---|---|---|---|---|
| 4×/2×/1× | 1:1 (v0.2) | yes | −23.19% | −24.10 / −22.28 | −7.85% | 2.95 | 2.27 |
| 4×/2×/1× | push | yes | +0.15% | −0.82 / +1.12 | +0.05% | 2.94 | 1.93 |
| **4×/2×/1×** | **push** | **no** | **+4.78%** | 4.13 / 5.43 | **1.53%** | 3.13 | 2.02 |
| 4×/2×/1× | 1:4 | no | −1.07% | −1.71 / −0.42 | −0.34% | 3.13 | 2.10 |
| 3×/2×/1× | push | yes | +5.61% | 4.61 / 6.60 | 2.16% | 2.60 | 1.58 |
| 3×/2×/1× | 1:4 | no | +4.46% | 3.79 / 5.12 | 1.61% | 2.77 | 1.75 |
| 3×/2×/1× | 1:4 | yes | −0.21% | −1.18 / +0.76 | −0.08% | 2.60 | 1.66 |
| **3×/1×/1×** | **1:2** | **no** | **+2.68%** | 2.51 / 2.85 | **0.97%** | 2.76 | 1.87 |
| 3×/1×/1× | 1:4 | yes | +4.06% | 3.61 / 4.52 | 1.59% | 2.55 | 1.68 |
| **2×/1×/1×** | **1:2** | **yes** | **+3.94%** | 3.51 / 4.37 | **1.80%** | 2.19 | 1.40 |
| 2×/1×/1× | 1:1 | no | −3.30% | −3.46 / −3.14 | −1.39% | 2.38 | 1.69 |

Full table (33 structures): `results_optimal.json`. Commonly quoted reference points: Ultimate Texas Hold'em ≈ 2.2% house edge / 0.5% element of risk; Mississippi Stud ≈ 4.9% / 1.4%; Three Card Poker (Ante) ≈ 3.4% / 2.0%.

## Key insights
1. **The river fold is worth ~4.6% to a perfect player** in 4×/2×/1× with a pushing Base. Removing it moves the game from break-even to +4.8%.
2. **Each step of Base payout (1:1 → 1:2 → 1:4 → push) is worth ~5–6%** to the house.
3. **Dropping the preflop raise from 4× to 3× is worth ~5%** to the house. A 3× raise with a 1× flop bet makes the flop decision meaningless when there is no fold (1× now or 1× later is the same).

## Options for a 2–5% house edge
- **A. 4×/2×/1×, Base pushes on a win, no river fold:** +4.8% / EoR 1.5%. Keeps the full "Ultimate" raise ladder; the Base never wins.
- **B. 3×/1×/1×, Base pays 1:2, no river fold:** +2.7% / EoR 1.0%. Closest to UTH economics; effectively one decision (3× now or 1× later).
- **C. 2×/1×/1×, Base pays 1:2, river fold allowed:** +3.9% / EoR 1.8%. Keeps the fold; smaller action.
- **D. (not yet computed) Option A plus a Base bonus paytable** (Base pays a bonus when the player wins with a strong hand, like UTH's Blind). Tune it to land around 2.5–3.5%. This is likely the most attractive design, but it needs one more engine run.
