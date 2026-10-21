# Decision Log
Append-only. One entry per design decision. To reverse a decision, add a new entry that supersedes it.

**Template**
```
## D-### — <short title>
- Date: YYYY-MM-DD
- Status: Proposed | Accepted | Superseded by D-###
- Rules version affected: v#.#
- Decision:
- Why:
- Evidence: (EXP-###, PT-###, reasoning)
- Alternatives considered:
- Revisit when:
```

---

## D-001 — Single Base wager + one optional Play raise
- Date: carried over from original concept draft; logged 2026-10-21
- Status: Accepted (provisional)
- Rules version affected: v0.1
- Decision: One mandatory Base wager plus one optional Play raise, instead of separate Ante and Blind wagers.
- Why: Ante + Blind would add qualification and paytable rules before the core concept is tested. A single wager is easier to explain, faster to settle, and keeps the Pai Gow identity.
- Evidence: Design reasoning only.
- Alternatives considered: UTH-style Ante + Blind + Play.
- Revisit when: Math v0.2 shows house edge needs a separate paytable wager.

## D-002 — Tie in either component = overall loss
- Date: carried over from original concept draft; logged 2026-10-21
- Status: Superseded by D-006
- Rules version affected: v0.1
- Decision: Player must WIN both components; any tie loses the whole wager. Only one-win/one-loss pushes.
- Why: Provides house edge in an even-money game with no dealer qualification. Explicitly supersedes an earlier, more permissive interpretation in the draft.
- Evidence: Design reasoning only. Not yet measured.
- Alternatives considered: Ties push (more permissive).
- Revisit when: Board-play tie frequency and overall EV are measured (v0.2).

## D-003 — Raise schedule 4× / 2× / 1× with fold only at river
- Date: carried over from original concept draft; logged 2026-10-21
- Status: Accepted (provisional)
- Rules version affected: v0.1
- Decision: One Play raise at 4× preflop, 2× after flop, or 1× after river; fold only at river.
- Why: Familiar Ultimate Texas Hold'em structure.
- Evidence: None yet. The draft flags it may be exploitable.
- Alternatives considered: Lower preflop cap (e.g., 3×).
- Revisit when: Optimal-strategy EV is computed (v0.2).

## D-004 — Provisional Hold'em-first dealer house way
- Date: carried over from original concept draft; logged 2026-10-21
- Status: Accepted as placeholder; must be replaced before launch
- Rules version affected: v0.1
- Decision: Dealer picks best two-card Hold'em hand (pair > suited > offsuit, by rank); rest go to Omaha.
- Why: Simple, deterministic, auditable for a first prototype.
- Evidence: None. Known to possibly weaken dealer Omaha.
- Alternatives considered: Equity-based six-card house way (planned).
- Revisit when: Simulator exists; compare house ways by simulation.

## D-005 — Six-seat cap, single deck, three burns; no side bets in v1
- Date: carried over from original concept draft; logged 2026-10-21
- Status: Accepted
- Rules version affected: v0.1
- Decision: Max six player spots; one 52-card deck; three burn cards. Side bets excluded until the base game is validated.
- Why: 6 × 7 + 8 = 50 cards fits one deck; seven players would need 56. Side bets would complicate early validation.
- Evidence: Card arithmetic.
- Revisit when: Operational v0.3 (alternative burn procedures, side-bet design).

## D-006 — A tie counts as a lost hand (not an automatic overall loss)
- Date: 2026-10-21
- Status: Accepted (provisional)
- Rules version affected: v0.2
- Decision: Each tied component is scored as a lost hand. Overall result = number of hands won: 2 = WIN, 1 = PUSH, 0 = LOSS. So Win + Tie and Tie + Win are PUSH.
- Why: Matias clarified this was the intended rule; the original draft's "any tie = overall loss" misstated it. It is also simpler to explain ("a tie loses that hand").
- Evidence: Design intent; EV impact to be measured.
- Alternatives considered: Any tie = overall loss (D-002, harsher); ties push that hand (more generous).
- Revisit when: Math shows the house edge with this rule.
