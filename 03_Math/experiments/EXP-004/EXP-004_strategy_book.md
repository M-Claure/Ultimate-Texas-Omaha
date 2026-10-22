# EXP-004 — Player strategy book for the chosen structure (D-010)

| Field | Value |
|---|---|
| Date | 2026-10-22 |
| Structure | 4× / 2× / 1× Play raise, Base pushes on a win, no river fold; dealer House Way H |
| Data | 12,000 hands solved optimally (all 15 splits, raise and check values; seeds 41,000,000+); 2,000 of them re-solved with independent random numbers (seed 77,000,000+) for unbiased split tests; 30,000 flop decisions (seed 52,000,000+); 2,000,000-hand simulation of the final book (seeds 61,000,000+) |
| Code | `src/uto/player_split.py` (split rule B1), `src/uto/book_rules.py` (preflop rule), `experiments/EXP-004/book_sim.py` (flop rule F1 + evaluation) |

## Optimal-play house edge (confirmation run)
Independent re-run on 12,000 hands (different engine settings): house edge between **4.20% and 4.97%**, which agrees with EXP-003's 4.13–5.43%. Best estimate **≈ 4.6%** per Base.

## How the book was derived
1. **Split.** Candidate rules were scored on the per-split optimal values. Comparing two fixed rules on the same hands is unbiased; a final check used independent random numbers. Main findings:
   - Playing like the dealer (House Way H) costs the player ~3.3%.
   - Players should always keep a pair in Hold'em, except a pair of Tens or lower when they also hold Ace-King.
   - With no pair and at most one card Queen or higher, the player should put **low** cards in Hold'em (keeping the strong cards together in Omaha). With an Ace, they should pair it with the lowest card of its suit.
   - Reason: the Base is only lost when the player loses **both** hands. One very strong hand protects the Base by turning many losses into pushes.
2. **Preflop.** A cost-weighted tree on human features (Hold'em pair rank, number of Omaha cards Ten or higher), simplified by hand. Cost vs optimal preflop decisions: ~0.6%.
3. **Flop.** Optimal rule: raise 2× when P(win both) > P(lose both). This was approximated with made-hand features. Cost: 1.3% per checked hand, ~0.9% overall.
4. **River.** No decision (1× is required).

## Book rules (v1)
See `UTO_Game_Book_v0.3.md` (repo root) for the player-facing version.

## Results
| Player | House edge | Element of risk | Avg total bet | Notes |
|---|---|---|---|---|
| Optimal play | ≈ 4.6% (4.2–5.0%) | ≈ 1.5% | 3.13 | EXP-003 / EXP-004 |
| **Strategy book v1** | **7.42% ± 0.27%** | 2.48% | 3.00 | 2M-hand simulation |
| Book split + dealer split rule instead of B1 | ≈ 8.5–9% (estimated) | | | split rule matters |

Book play frequencies: 4× preflop 27.4%, 2× flop 17.3%, 1× river 55.2%. Outcomes: win 23.0%, push 51.9%, loss 25.0%.

## Next improvements (optional)
- A better no-pair split rule could recover up to ~1.5%.
- Richer flop rules (draws, Omaha two pair) could recover up to ~0.9%.
