# EXP-002 — Dealer-friendly house way + payout/raise structures

| Field | Value |
|---|---|
| Date | 2026-10-21 |
| Rules version tested | v0.2 (tie = lost hand), with payout/raise variants in part 2 |
| Code | `03_Math/src/uto/` (`house_way.py` SIMPLE rules, `strategy2.py`); scripts in this folder |
| Seeds | house ways: deals 13,000,000+i (2M hands), oracle 950,000,000+i · structures: deals 11,000,000+i, MC 800,000,000+i (300k hands) · noise check: 17,000,000+i |
| Why | Matias rejected rule C (EXP-001): a dealer can't compute equities at the table. Goal: a rule a dealer can apply in seconds, and a structure with a small house edge. |

## Part 1 — Dealer-friendly house ways (flat Base bet, 2M hands each, same deals)

**House Way H (recommended):**
1. **Trips or quads:** two of them go to Hold'em.
2. **Two pairs (or three):** the highest pair goes to Hold'em.
3. **One pair:**
   - 9s or higher → the pair goes to Hold'em.
   - 2s through 8s → the pair goes to Hold'em, **unless** the dealer also holds two other cards that are both Jack or higher; then those two go to Hold'em.
4. **No pair:** the two highest cards go to Hold'em.
5. **Suits:** when there is a choice of which suit goes to Hold'em, keep same-suited cards together in the Omaha hand.

| Dealer rule | House edge vs player C w=0.75 | vs player C w=1.0 | vs player A | Gap to rule C (paired) |
|---|---|---|---|---|
| A v0.1 Hold'em-first | +0.85% | +0.99% | +2.05% | −1.4% |
| S1 pair → Hold'em, else two highest | +1.67% | +1.73% | +2.39% | −0.6% |
| S2 = S1 + small-pair switch (2s–8s / J+) | +2.19% | +2.16% | +2.56% | −0.1% to −0.2% |
| **H = S2 + keep Omaha suited** | **+2.25%** | **+2.23%** | **+2.62%** | **−0.04% to −0.17%** |
| C weighted w=0.5 (EXP-001, not dealer-usable) | +2.29% | +2.40% | +3.18% | 0 |

±95% on each edge ≈ 0.10%; on each paired gap ≈ 0.04–0.05%. Oracle − H on 100k paired hands: +0.42% ± 0.20%.

How H was found: rule C's choices were tabulated by hand type. C keeps any pair of 7s+ in Hold'em; with a small pair it switches to two high cards once both are about Jack or better; with no pair it plays the two highest cards ~75% of the time; with trips it almost always puts two of the trips in Hold'em. v0.1's "suited before offsuit" ordering was the main weakness of rule A (no-pair hands agreed with C only 40% of the time).

## Part 2 — Payout / raise structures (with raises), dealer uses H
Player model: at each betting point the player knows Monte Carlo estimates of P(win) and P(loss); raises preflop / on the flop when P(win) − P(loss) beats a threshold (thresholds grid-searched on half the hands, scored on the other 150k); river call/fold by exact EV. This player is good but not perfectly optimal, so house edges are slight **over**-estimates. Noise check: 4× more rollouts lowered the house edge by only 0.2–0.5%.

Base: lost on an overall loss, returned on a push. "Base on win" = what the Base pays when the player wins both hands. Play bet always pays 1:1.

| Raises (pre / flop / river) | Base on win | River fold? | House edge (per Base) | ±95% | Element of risk | Avg total bet |
|---|---|---|---|---|---|---|
| 4× / 2× / 1× (current v0.2) | 1:1 | yes | **−21.1%** | 1.1% | −7.2% | 2.93 |
| 4× / 2× / 1× | 1:1 | no | −16.0% | 1.2% | −5.2% | 3.07 |
| 4× / 2× / 1× | 1:2 | yes | −9.5% | 1.1% | −3.2% | 2.93 |
| 4× / 2× / 1× | 1:4 | no | +1.5% | 1.1% | +0.5% | 3.07 |
| **4× / 2× / 1×** | **push** | **yes** | **+2.1%** | 1.0% | **+0.7%** | 2.92 |
| 4× / 2× / 1× | push | no | +7.4% | 1.0% | +2.4% | 3.07 |
| 3× / 2× / 1× | 1:4 | yes | +1.6% | 0.8% | +0.6% | 2.55 |
| 3× / 1× / 1× | 1:2 | yes | +0.3% | 0.9% | +0.1% | 2.51 |
| 2× / 1× / 1× | 1:1 | no | −0.8% | 0.9% | −0.3% | 2.37 |

All 40 structures are in `results_structures.json`. Reference point: Ultimate Texas Hold'em is commonly quoted at about 2.2% house edge per Ante and about 0.5% element of risk.

## Conclusions
1. **House Way H** is dealer-usable (a five-line rule) and gives up only ~0.1–0.2% versus the best computed split, and it beats the v0.1 rule by ~1.4% of Base.
2. Under the current payouts the player wins big; no house way fixes that.
3. The lever that matters is **what the Base pays when the player wins**. Keeping the familiar 4×/2×/1× raises with a river fold, and making the Base **push** on a win, gives roughly **+2% house edge, 0.7% element of risk**, close to Ultimate Texas Hold'em's economics. Smaller raises with a reduced Base payout reach similar edges.
4. A Base that never wins may feel bad to players. The standard fix (as in UTH's Blind bet) is a **bonus paytable on the Base for strong winning hands**. It returns some value to the player in an exciting way. It needs a slightly harsher base structure (e.g., no river fold) so the edge stays around 2–4%.

## Next steps (proposed)
- EXP-003: design a Base bonus paytable (pays when the player wins with strong hands) on top of a structure with ~5–7% edge, tuned back to a ~2–4% target.
- Replace the threshold player with a fully optimized strategy for the final numbers.
- Distill the player's optimal split into a "player strategy card" (players also need guidance).
