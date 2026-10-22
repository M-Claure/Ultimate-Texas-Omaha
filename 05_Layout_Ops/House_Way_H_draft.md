# Dealer House Way H (draft, proposed — D-008)

The dealer sets six cards into a 2-card **Hold'em** hand and a 4-card **Omaha** hand, before the flop, using these steps in order. Use the first step that applies.

1. **Three or four of a kind:** put **two of them** in Hold'em.
2. **Two pairs (or three pairs):** put the **highest pair** in Hold'em.
3. **One pair:**
   - **9s or higher:** put the pair in Hold'em.
   - **2s through 8s:** put the pair in Hold'em, **unless** you also hold **two other cards that are both Jack or higher**. In that case, put those two cards in Hold'em.
4. **No pair:** put the **two highest cards** in Hold'em.
5. **Suits:** if you could use either of two cards of the same rank, choose so that **same-suited cards stay together in the Omaha hand**. If it still doesn't matter, use the higher suit (♠ > ♥ > ♦ > ♣) in Hold'em.

All remaining cards form the Omaha hand.

## Examples
| Dealer's six cards | Hold'em | Omaha | Why |
|---|---|---|---|
| 5♣ 5♦ A♠ K♥ 9♣ 2♦ | A♠ K♥ | 5♣ 5♦ 9♣ 2♦ | Small pair, and A and K are both J or higher |
| 5♣ 5♦ A♠ T♥ 9♣ 2♦ | 5♣ 5♦ | A♠ T♥ 9♣ 2♦ | T is below Jack → keep the pair |
| 9♣ 9♦ A♠ K♥ 7♣ 2♦ | 9♣ 9♦ | A♠ K♥ 7♣ 2♦ | 9s or higher → pair |
| 9♣ 9♦ 4♠ 4♥ A♣ 2♦ | 9♣ 9♦ | 4♠ 4♥ A♣ 2♦ | Two pairs → highest pair |
| A♣ J♦ 9♠ 7♥ 4♣ 2♦ | A♣ J♦ | 9♠ 7♥ 4♣ 2♦ | No pair → two highest |

Performance (EXP-002): within ~0.1–0.2% of the best computed split; ~1.4% of Base better than the v0.1 house way.
