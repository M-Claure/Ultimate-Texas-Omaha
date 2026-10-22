# Ultimate Texas Omaha — Game Book (v0.3 draft)

*Working title. Prototype math, not yet independently certified. Prepared 2026-10-22; strategy book updated to v2 the same day.*

## 1. The game in one paragraph
A house-banked poker game. The player and the dealer each get six cards and split them into a **2-card Texas Hold'em hand** and a **4-card Omaha hand**. Both hands play against the same five community cards. The player raises once, at most, as the board comes out: **4× before the flop, 2× on the flop, or 1× at the river**. To win, the player must beat the dealer with **both** hands. Winning one and losing the other is a push. A tie counts as a lost hand.

## 2. Rules (Rules v0.3 draft)
1. **Wager:** the player places a **Base** bet (1 unit).
2. **Deal:** player and dealer each receive 6 cards face down (one 52-card deck, max 6 players).
3. **Set hands:** the player puts 2 cards in the Hold'em box and 4 in the Omaha box. The split is locked before the flop. The dealer sets their hand by the **House Way** (Section 3).
4. **Betting (one Play raise per hand):**
   - Before the flop: raise **4×** the Base, or check.
   - After the flop (if no raise yet): raise **2×**, or check.
   - After the turn and river (if no raise yet): the player **must bet 1×**. There is no fold.
5. **Showdown:**
   - Hold'em hand: best 5 cards from its 2 cards + the 5 board cards (may play the board).
   - Omaha hand: exactly 2 of its 4 cards + exactly 3 board cards.
   - Each player hand is compared with the dealer's matching hand. **A tie counts as a lost hand.**
6. **Settlement:**

| Player wins… | Result | Base | Play |
|---|---|---|---|
| both hands | **WIN** | **pushes** | pays 1:1 |
| exactly one hand | PUSH | pushes | pushes |
| neither hand | LOSS | loses | loses |

*Example:* Base $10, raise 4× ($40). Win both → +$40. Win one → $0. Lose both → −$50.

## 3. Dealer House Way (H)
Use the first step that applies:
1. **Three or four of a kind:** two of them go to Hold'em.
2. **Two or three pairs:** the highest pair goes to Hold'em.
3. **One pair:**
   - 9s or higher: the pair goes to Hold'em.
   - 2s through 8s: the pair goes to Hold'em, unless the dealer also has two other cards both Jack or higher. Then those two go to Hold'em.
4. **No pair:** the two highest cards go to Hold'em.
5. **Suits:** when there's a choice, keep same-suited cards together in Omaha.

## 4. Player strategy (Book v2)

### 4.1 Setting your hand
1. **Three or four of a kind:** two of them in Hold'em.
2. **Two or three pairs:** your highest pair in Hold'em.
3. **One pair:** the pair in Hold'em. *Exception:* if your pair is **Tens or lower** and you also hold an unpaired **Ace and King**, put **A-K** in Hold'em.
4. **No pair:**
   - (a) If your second-highest card is a **Queen or higher**, put your **two highest** cards in Hold'em.
   - (b) Otherwise, if your highest card is an **Ace or King**, put it in Hold'em with the **lowest card of the same suit**. If no card matches its suit, use your lowest card.
   - (c) Otherwise, put your **two lowest** cards in Hold'em.
5. **Suits:** when there's a choice, keep same-suited cards together in Omaha.

*Why low cards?* You only lose the Base when you lose **both** hands. A very strong Omaha hand (your four best cards) protects you by turning many losses into pushes.

### 4.2 Before the flop — raise 4× with:
- a Hold'em pair of **Jacks or better**;
- **Tens** if two or more of your Omaha cards are Ten or higher;
- **Nines** if three or more of your Omaha cards are Ten or higher;
- **Ace-King** if two or more of your Omaha cards are Ten or higher.

Otherwise check.

### 4.3 On the flop — raise 2× if any of these is true:
- your **Omaha** hand already has **three of a kind or better** (using exactly 2 of its cards);
- the flop is **unpaired** and your **Hold'em** hand has **top pair or better** (top pair, an overpair, two pair or better), and the flop's highest card is **8 or higher** (on lower flops you need **two pair or better**);
- the flop is **unpaired**, your **Omaha** hand has **two pair** and your **Hold'em** hand has any pair using one of its own cards;
- the flop is **paired** and your **Hold'em** hand has **three of a kind or better**.

Otherwise check.

### 4.4 At the river
If you haven't raised, bet 1× (required).

## 5. The math

### 5.1 House edge
| Player | House edge (per Base) | Element of risk | Average total bet |
|---|---|---|---|
| **Perfect play** | **≈ 4.6%** (true value between 4.2% and 5.0%) | ≈ 1.5% | 3.13 units |
| Following this book (v2) | 7.3% (± 0.3%) | 2.4% | 3.04 units |

Commonly quoted for comparison: Ultimate Texas Hold'em ≈ 2.2% / 0.5%, Three Card Poker (Ante) ≈ 3.4% / 2.0%, Mississippi Stud ≈ 4.9% / 1.4%.

### 5.2 What happens under perfect play
| Final bet | How often | Win (net) | Push | Loss (net) |
|---|---|---|---|---|
| Raised 4× preflop | 30.2% | 10.2% (+4) | 15.3% (0) | 4.7% (−5) |
| Raised 2× on flop | 22.4% | 7.5% (+2) | 12.1% (0) | 2.8% (−3) |
| Bet 1× at river | 47.4% | 5.8% (+1) | 24.6% (0) | 17.1% (−2) |
| **Total** | 100% | **23.5%** | **52.0%** | **24.6%** |

Standard deviation per hand ≈ 2.0 units.

### 5.3 What happens following the book v2 (2,000,000 simulated hands)
| Final bet | How often | Win | Push | Loss |
|---|---|---|---|---|
| 4× preflop | 27.4% | 34.5% | 50.3% | 15.2% |
| 2× flop | 21.9% | 31.2% | 55.3% | 13.5% |
| 1× river | 50.7% | 13.6% | 50.8% | 35.6% |
| **All hands** | | **23.2%** | **51.6%** | **25.1%** |

## 6. How these numbers were calculated
- **Hand evaluation:** custom evaluators, cross-checked on 40,000 random comparisons against an independent open-source evaluator.
- **Perfect play:** solved backwards (river → flop → preflop → split) for 30,000 + 12,000 random player hands. Probabilities come from Monte Carlo over the unseen cards. Sampled river probabilities match a full enumeration of all 4,496,388 dealer hands.
- **Error bars:** the "perfect play" figure is bracketed. One estimate slightly flatters the player and one slightly understates them, so the true value lies between. Sampling error is about ±0.2%.
- Details: `03_Math/experiments/EXP-003`, `EXP-004` and `EXP-005`.

## 7. Playtest kit
Printable mats, dealer card, player rules sheet and session log: `04_Playtests/kit/`.

## 8. Open items
- **Certification:** independent math certification is required before any casino trial.
- **Player appeal:** test whether players accept a Base that never wins outright and a required river bet. A Base bonus paytable for strong hands is a possible future add-on.
- **Strategy book:** v2 gives up ~2.7% versus perfect play. Most of this is in the split (~1.4%), which depends on fine suit and connectivity details that simple rules can't capture (EXP-005). Quote the optimal-play figure to regulators, and expect real players to give the house 7–8% or more.
- **Assumptions:** figures assume one player against the dealer. Multi-player card removal effects are expected to be small.
