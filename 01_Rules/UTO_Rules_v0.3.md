# Ultimate Texas Omaha — Rules of Play v0.3

| Field | Value |
|---|---|
| Version | v0.3 (draft) |
| Status | PROTOTYPE — math by simulation (EXP-003/004); not independently certified |
| Effective date | 2026-10-22 |
| Supersedes | `UTO_Rules_v0.2.md` (payouts, river fold and house way changed — D-008, D-010) |
| Author | Matias |

## 1. Overview
House-banked poker. Six private cards are split into a 2-card Hold'em hand and a 4-card Omaha hand, played against one shared five-card board. The wager wins only if both hands beat the dealer. A tie counts as a lost hand. One hand won = push; no hands won = loss.

## 2. Equipment and table
- 2.1 One standard 52-card deck, no jokers.
- 2.2 Maximum six player spots. Three burn cards (6 × 7 + 5 + 3 = 50 cards).
- 2.3 Each spot has a Hold'em (2-card) box, an Omaha (4-card) box, a Base circle and a Play circle.

## 3. Wagers
- 3.1 **Base:** mandatory, 1 unit, placed before the deal.
- 3.2 **Play:** exactly one per hand, made at the first of these points the player chooses:

| Decision point | Options |
|---|---|
| Preflop (after locking the split) | Bet 4× Base, or check |
| After the flop (if no Play bet yet) | Bet 2× Base, or check |
| After the river (if no Play bet yet) | **Must bet 1× Base** (no fold) |

- 3.3 Once made, the Play bet cannot be changed or withdrawn.

## 4. Dealing and hand setting
- 4.1 Each player and the dealer receive six cards face down.
- 4.2 Each player places exactly two cards in Hold'em and four in Omaha before the flop. The split is locked.
- 4.3 The dealer sets their hand by the House Way (Section 7) before any board card is revealed.
- 4.4 Burn and flop (3 cards); burn and turn; burn and river.

## 5. Hand evaluation
- 5.1 Standard five-card poker rankings.
- 5.2 Hold'em: best five of its 2 cards + 5 board cards, any combination (may play the board).
- 5.3 Omaha: exactly two of its 4 cards + exactly three board cards.
- 5.4 Compare Hold'em with Hold'em and Omaha with Omaha. **A tie is a lost hand for the player.**

## 6. Settlement
| Hands the player wins | Result | Base | Play |
|---|---|---|---|
| 2 | WIN | push (returned) | pays 1:1 |
| 1 | PUSH | push | push |
| 0 | LOSS | loses | loses |

## 7. Dealer House Way (H)
First applicable step:
1. Three or four of a kind: two of them to Hold'em.
2. Two or three pairs: highest pair to Hold'em.
3. One pair: 9s or higher → the pair to Hold'em. 2s–8s → the pair to Hold'em, unless the dealer also holds two other cards both Jack or higher; then those two go to Hold'em.
4. No pair: the two highest cards to Hold'em.
5. Suits: when there's a choice, keep same-suited cards together in Omaha; otherwise put higher suits (♠ > ♥ > ♦ > ♣) in Hold'em.

## 8. Examples (Base = $10)
| Play bet | Result | Net |
|---|---|---|
| 4× ($40) | Win both | +$40 (Base returned) |
| 2× ($20) | Win Hold'em, lose Omaha | $0 |
| 1× ($10) | Win Hold'em, tie Omaha | $0 (tie = lost hand → one win → push) |
| 1× ($10) | Lose both | −$20 |

## 9. Math summary
House edge ≈ 4.6% of the Base under perfect play (range 4.2–5.0%); element of risk ≈ 1.5%. See `UTO_Game_Book_v0.3.md`.
