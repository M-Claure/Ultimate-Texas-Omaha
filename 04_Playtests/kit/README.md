# UTO Playtest Kit (Rules v0.3, strategy book v2)

| File | What it is | Print |
|---|---|---|
| `UTO_Player_Rules_Sheet.pdf` | Front: how to play, payouts, examples. Back: how to play your hand (strategy book v2) | 1 per player, double-sided, letter |
| `UTO_Player_Mat.pdf` | Hold'em box (2 cards), Omaha box (4 cards), Base circle, Play box, payout reminder | 1 per seat, letter landscape |
| `UTO_Dealer_Mat.pdf` | Board (flop/turn/river), dealer Hold'em and Omaha boxes | 1, letter landscape |
| `UTO_Dealer_Card.pdf` | Procedure, House Way H with examples, settlement table | 1 for the dealer |
| `UTO_Session_Log.pdf` | Page 1: hand-by-hand log. Page 2: player feedback form | Page 1 ×2–3 per session; page 2 one per player |

Regenerate: `python3 make_kit.py .` and `python3 make_rules_sheet.py .` (needs `reportlab`). Strategy text is in `strategy_text.py`.

## Running a session (checklist)
1. **Before:** each player signs the NDA and goes in `00_Admin/Disclosure_Log.md`. Create `04_Playtests/sessions/PT-###_YYYY-MM-DD.md` from the template in `Playtest_Index.md`.
2. **Supplies:** 1 deck (+1 spare), chips or tokens (Base = 1 chip), timer/phone, printed kit.
3. **Teach (≤5 min):** walk through the rules sheet front. Hand out the back (strategy) after 10 hands, so you can see how intuitive the game is without help.
4. **Play 50–100 hands.** You (or a volunteer) deal, using the dealer card for House Way H. Log every hand on the session log, including how long each player takes to set their split.
5. **After:** collect feedback forms, enter results in the PT log and `Playtest_Index.md`, and commit.

## What to measure
- Average time to set the split; hands per hour.
- Dealer errors (house way, settlement).
- Rule questions and confusion points.
- Reactions to: frequent pushes, tie = lost hand, Base never winning, required river bet.
- How often players deviate from the strategy sheet.
