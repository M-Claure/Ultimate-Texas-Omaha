# EXP-001 — Dealer split (house way) tournament

| Field | Value |
|---|---|
| Date | 2026-10-21 |
| Rules version tested | v0.2 (tie = lost hand) |
| Code | `03_Math/src/uto/` at the commit that adds this file; scripts in this folder |
| Seeds | flat: deals 1,000,000+i, oracle 900,000,000+i · grid: 3,000,000+i · raise preview: 5,000,000+i, MC 700,000,000+i |
| Hands | 2,000,000 per flat matchup · 100,000 for the oracle · 1,000,000 per grid cell · 100,000 per raise preview |
| Setup | Heads-up (1 player vs dealer). Equity tables: `03_Math/data/equity_tables.npz` (seed 20261021) |

## Question
Which dealer split rule gives the house the most edge, and how much does the choice matter?

## Rules compared
"Equity" = chance a hand beats one random hand of the same type on a random board (from the equity tables). Dealer counts ties as wins (a tie is a lost hand for the player).

| Rule | Definition |
|---|---|
| Random | Random split (baseline) |
| A | Rules v0.1 house way: best 2-card Hold'em (pair > suited > offsuit, by rank) |
| B | Omaha-first: the 4 cards with the best Omaha equity go to Omaha |
| C (w) | Pick the split with the highest `Hold'em equity + w × Omaha equity` |
| D | Oracle: for each dealer hand, simulate all 15 splits (300 rollouts) against the reference player and take the best |

Players split with the same families (A, B, C). Best player found: C with w ≈ 0.6–0.75.

## Results 1 — flat bet (Base only, no raises, no folds), player = C w=1, 2M hands
| Dealer rule | House edge | ±95% | Player win | Push | Player loss |
|---|---|---|---|---|---|
| Random | −14.31% | 0.10% | 31.4% | 51.4% | 17.1% |
| B Omaha-first | −12.43% | 0.09% | 28.5% | 55.5% | 16.0% |
| A Hold'em-first (v0.1) | +0.99% | 0.10% | 23.9% | 51.3% | 24.9% |
| C w=1.0 | +1.89% | 0.10% | 23.4% | 51.3% | 25.3% |
| C w=0.75 | +2.30% | 0.10% | 23.2% | 51.2% | 25.6% |
| **C w=0.5** | **+2.44%** | 0.10% | 23.2% | 51.1% | 25.7% |
| D Oracle (100k hands) | +2.78% | 0.43% | 22.8% | 51.7% | 25.6% |

Paired on the same 100k hands, **Oracle − C(w=0.5) = −0.04% ± 0.20%**: the simple weighted rule captures essentially all of the oracle's value. Oracle − A = +1.44% ± 0.25%.

## Results 2 — dealer weight vs player's best response (1M hands per cell)
Against every player weight tried (0.25–1.0), dealer C with w between 0.25 and 0.6 gives a flat edge of ~2.3–2.5%; dealer A gives ~0.85–1.0%. The player's best response is w ≈ 0.6–0.75 (flat edge ≈ 2.3% vs dealer C w=0.5).

## Results 3 — preview WITH raises (simple, non-optimal player strategy S1)
S1: raise 4× preflop if Monte Carlo EV > threshold; otherwise check to the river and call 1× if EV > −0.5, else fold. No 2× flop raises. Because S1 is not optimal, these are **upper bounds** on the house edge (the real edge is even lower).

| Dealer rule | Best S1 threshold | House edge (per Base) | ±95% | Element of risk | 4× raise rate | Fold rate |
|---|---|---|---|---|---|---|
| A (v0.1) | 0.00–0.05 | **−20.4%** | 1.5% | −6.5% | 42% | 12% |
| C w=0.5 | 0.00–0.05 | **−16.8%** | 1.5% | −5.6% | 38% | 13% |

Calibration check: S1's EV estimates match actual outcomes within ~0.01–0.03 across EV buckets (no information leak).

## Conclusions
1. **Dealer split:** rule C with w ≈ 0.5 (weight Hold'em equity about twice Omaha equity) is the best simple house way found. It matches the oracle within noise and beats the v0.1 house way by ~1.4–1.5% of Base. Hold'em equity matters more because Hold'em starting hands vary much more in strength than 4-card Omaha hands.
2. Random or Omaha-first splits are disastrous (−12% to −14%): the house way matters a lot.
3. **The bigger problem is not the split.** With even-money payouts on both Base and Play, a player using a simple strategy has an edge of roughly **17% of the Base** (and the true optimal edge is higher). Six private cards give the player lots of information before the 4× decision. No dealer split can fix this; the betting/payout structure must change.

## Next steps (proposed)
- Rebalance the economics (candidate levers): smaller max raise (e.g., 3× or 2×), Base pays less than even money or only pays on certain wins (like UTH's Ante/Blind), removing the river fold, or dealer qualification changes. Evaluate each with S1 first, then with an optimized strategy (EXP-002).
- Build the optimized player strategy (flop 2× decisions, better thresholds) for the final house edge.
- Multi-player card removal (up to 6 players) — small effect, check later.
