# Ultimate Texas Omaha — Rules of Play v0.1

| Field | Value |
|---|---|
| Version | v0.1 |
| Status | **PROTOTYPE — not for real-money play.** Payouts, house edge, optimal strategy, dealer house way and regulatory suitability are unvalidated. |
| Effective date | 2026-10-21 |
| Supersedes | `archive/Ultimate_Texas_Omaha_Concept.docx` (original concept draft; content carried over unchanged in substance) |
| Author | Matias |

---

## 1. Overview
A house-banked poker game combining a six-card Texas Hold'em / Omaha split with Pai Gow-style aggregate settlement and staged, Ultimate Texas Hold'em-style raises. Each participant receives six private cards and locks two for Hold'em and four for Omaha before the flop. Both hands play against the same five-card board. The wager wins only if **both** hands beat the dealer; a split decision pushes; any tie loses.

## 2. Equipment and table
- 2.1 One standard 52-card deck, no jokers.
- 2.2 Maximum **six** player spots. Card budget: 6 × (players + dealer) + 5 board + 3 burns = 6 × 7 + 8 = 50 cards. A seventh player would require 56.
- 2.3 Each spot has a marked **Hold'em (2-card)** box, an **Omaha (4-card)** box, a **Base** circle and a **Play** circle.

## 3. Wagers
- 3.1 **Base:** mandatory 1 unit, placed before cards are dealt.
- 3.2 **Play:** optional single raise. Size depends on when it is made:

| Decision point | Options |
|---|---|
| Preflop (after locking the split) | Raise 4× Base, or check |
| After flop (only if no raise yet) | Raise 2× Base, or check |
| After turn and river (only if no raise yet) | Raise 1× Base, or **fold** |

- 3.3 Only one Play raise per hand. Once placed it cannot be changed or withdrawn.
- 3.4 Folding forfeits the Base. (No Play wager exists at that point.)

## 4. Dealing and hand setting
- 4.1 Each player and the dealer receive six cards face down.
- 4.2 Each player splits exactly two cards to Hold'em and four to Omaha, and places them in the matching boxes. The split is **locked before the flop**; no later changes. A physical lock-in gesture confirms the split.
- 4.3 The dealer sets their hand using the house way (Section 7) before any board card is revealed.
- 4.4 Burn one card and reveal three flop cards; burn and reveal the turn; burn and reveal the river (three burns total).

## 5. Hand evaluation
- 5.1 Standard five-card poker rankings and kickers.
- 5.2 **Hold'em hand:** best five cards from the two Hold'em hole cards plus the five board cards, using any combination (two, one, or zero hole cards).
- 5.3 **Omaha hand:** best five cards using **exactly two** of the four Omaha hole cards and **exactly three** board cards.
- 5.4 Each player hand is compared with the dealer's corresponding hand (Hold'em vs Hold'em, Omaha vs Omaha).

## 6. Settlement
"Tie" = exactly equal hand strength in that component.

| Hold'em | Omaha | Overall |
|---|---|---|
| Win | Win | **WIN** |
| Win | Lose | PUSH |
| Lose | Win | PUSH |
| Win | Tie | LOSS |
| Tie | Win | LOSS |
| Lose | Tie | LOSS |
| Tie | Lose | LOSS |
| Tie | Tie | LOSS |
| Lose | Lose | LOSS |

- 6.1 **Overall win:** Base and Play each pay 1:1.
- 6.2 **Overall push:** Base and Play returned.
- 6.3 **Overall loss:** Base and Play lost.
- 6.4 There is no dealer qualification requirement.

## 7. Dealer house way (provisional)
The dealer never chooses freely.
1. Enumerate all 15 two-card Hold'em selections from the dealer's six cards.
2. Rank them: (a) pocket pairs, higher pair first; (b) suited non-pairs, higher top card, then higher second card; (c) offsuit non-pairs, same ordering.
3. Remaining tie-break: suit order ♠ > ♥ > ♦ > ♣, comparing the two selected cards in descending rank/suit order.
4. The top-ranked selection is the Hold'em hand; the remaining four cards form the Omaha hand.

This rule is auditable but **not** optimal and may systematically weaken dealer Omaha. To be replaced by an equity-based house way before launch (see Decision D-004).

## 8. Examples (Base = $10)
| Action | Result | Outcome |
|---|---|---|
| Raise 4× preflop ($40 Play) | Hold'em win, Omaha win | Win: +$50 profit, $50 stake returned |
| Raise 2× after flop ($20 Play) | Hold'em win, Omaha lose | Push: $30 returned, $0 profit |
| Raise 1× at river ($10 Play) | Hold'em win, Omaha tie | Loss: −$20 |
| Check, check, fold at river | — | Loss: −$10 Base |

---

## Appendix A — Known open questions (not rules; to be resolved in later versions)
- A1. **Board-play ties.** When both the player's and dealer's best Hold'em hand is the board, the Hold'em component ties and the whole wager loses. Frequency unknown — measure in v0.2.
- A2. Is the tie-equals-loss rule too harsh for players, and does the 4× raise compensate? Requires optimal-strategy EV.
- A3. Should there be a paytable bonus (e.g., premium hands) or a non-even-money payout on Base?
- A4. Is 4×/2×/1× exploitable given the extra information from six cards?
- A5. Push frequency and its effect on player excitement and revenue per hour.
- A6. Equity-based dealer house way design.
