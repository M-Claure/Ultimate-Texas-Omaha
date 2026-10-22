# EXP-005 — Strategy book v2

| Field | Value |
|---|---|
| Date | 2026-10-22 |
| Rules | v0.3 (4×/2×/1×, Base pushes on a win, no river fold, House Way H) |
| Data | 36,000 optimally solved hands (EXP-004 `run_book_hands.py`, chunks 0–35, seeds 41,000,000+); rules learned on chunks 2–35 and checked out-of-sample on 2,000 hands re-solved with independent random numbers; 40,000 new flop decisions (seed 54,000,000+); 2,000,000-hand simulation of the final book (seeds 61,000,000+, same deals as the v1 test) |
| Scripts | this folder (`np_search.py`, `ptree.py` no-pair split; `op_tree.py` one pair; `tp.py` two pair; `pre3.py` preflop; `flop2.py`/`flop3.py` flop), `../EXP-004/book_sim.py v2` |

## What changed from v1
| Part | v1 | v2 |
|---|---|---|
| No-pair split | Ace → Ace + lowest card of its suit | **Ace or King** → that card + lowest card of its suit |
| Flop 2× | Omaha trips+; HE top pair+ (flop high card 8+, else two pair+); paired flop HE trips+ | v1 **plus:** unpaired flop, Omaha two pair and Hold'em any pair using one of its own cards |
| Preflop 4× | JJ+, TT with 2+ Omaha T+, 99 with 3+, AK with 2+ | unchanged (a grid search over 288 variants found nothing better) |

## Results (2,000,000 hands each, same deals)
| Book | House edge | ±95% | Element of risk | Avg total bet | 4× / 2× / 1× |
|---|---|---|---|---|---|
| v1 | 7.42% | 0.27% | 2.48% | 3.00 | 27.4% / 17.3% / 55.2% |
| **v2** | **7.31%** | 0.27% | **2.40%** | 3.04 | 27.4% / 21.9% / 50.7% |
| Optimal play | ≈ 4.6% (4.2–5.0%) | | ≈ 1.5% | 3.13 | 30.2% / 22.4% / 47.4% |

## Where the remaining ~2.7% goes (v2 vs optimal)
- **Split: ~1.4%.** Measured out of sample: optimal-ish splits beat B2 by 1.43%. No simple rule family captured it. Value-optimised policy trees up to depth 4 gained ≤0.15% more and were too complex to memorise. The optimal split depends on fine suit and connectivity details.
- **Flop: ~0.8%.** 1.13% per checked hand. The best tree on the same features would still lose ~0.87%.
- **Preflop: ~0.5%.**

## Conclusion
v2 is a small, cheap improvement (−0.11% house edge). The book is close to the limit of what can be memorised with rank and pair rules. Commercial and regulatory documents should quote the **optimal-play house edge (≈ 4.6%)**. Expect real players to give the house about **7–8%** or more.
