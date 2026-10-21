# UTO Roadmap — from concept to casino floor
Created 2026-10-21. Living plan: update status as work completes; record schedule changes in the Invention Log.
Timelines assume part-time work alongside school. Weeks are counted from 2026-10-26.

**Owners:** **M** = Matias (decisions, people, legal, money) · **C** = Claude (code, analysis, documentation, drafts)

---

## The big picture
| Phase | What it answers | Rough timing | Gate to pass before moving on |
|---|---|---|---|
| 0. Housekeeping & IP hygiene | Do you own this, and is it protected while you test? | Week 1 | Ownership clear; disclosure rules in place |
| 1. Math v0.2 | Does the game make money for the house without being unbeatable or unfair? | Weeks 1–6 | **Gate 1:** a rule set with a sensible house edge and no exploit |
| 2. Private playtests | Is it fun, understandable and fast enough? | Weeks 3–8 (parallel) | **Gate 2:** players get it and want to keep playing |
| 3. Rules v0.2 + final house way | Lock the game | Weeks 6–9 | Rules frozen for IP filing |
| 4. IP protection | Can it be protected, and is it new? | Weeks 8–12 | **Gate 3:** provisional filed (or decision not to) |
| 5. Operational v0.3 | Can a real dealer run it at speed? | Weeks 10–16 | Dealer procedures + layout + rack card done |
| 6. Commercial path | License to a distributor or go for approval yourself | Month 4+ | **Gate 4:** route chosen |

---

## Phase 0 — Housekeeping & IP hygiene (Week 1)
| # | Task | Owner | Done when |
|---|---|---|---|
| 0.1 | Fill in the conception date and contributors in `00_Admin/Invention_Log.md` | M | Entry filled, committed |
| 0.2 | Read the Aprende internship agreement for invention-assignment / outside-work clauses | M | Note in `IP_Checklist.md` |
| 0.3 | Check Northwestern's student IP policy (relevant if university resources are used) | M | Note in `IP_Checklist.md` |
| 0.4 | Draft a simple playtest NDA template | C drafts, M reviews | `00_Admin/NDA_Template.md` |
| 0.5 | Quick prior-art pass (Google Patents / USPTO search on the terms in `06_Prior_Art/`) | C searches, M reviews | ≥10 entries in Prior-Art Log |
| 0.6 | Rule: no public posts, videos or forum questions describing the game | M | Ongoing |

## Phase 1 — Math v0.2 (Weeks 1–6) — the most important phase
Nothing else matters if the math doesn't work. Code lives in `03_Math/src/` (Python first; port hot loops to C/C++ if speed demands).

| # | Task | Owner | Done when |
|---|---|---|---|
| 1.1 | Hand evaluator: 5-card ranks, Hold'em best-of-7, Omaha exactly-2+3; cross-check against an established open-source evaluator | C | Unit tests pass incl. ties, wheel straights, board-play Hold'em |
| 1.2 | Game engine: shuffle/deal (seeded), dealer house way v0.1, settlement matrix, wager accounting | C | Reproduces all Rules v0.1 examples |
| 1.3 | **EXP-001 Baseline:** simple fixed strategies (e.g., always 4×; never raise + always call 1×) → win/push/loss rates, tie rates, board-play-tie rate, rough EV | C | Results in Results Index; first read on viability |
| 1.4 | **Player split strategy:** for each hand choose the best of 15 splits by Monte Carlo equity vs. the dealer | C | Split rule + measured cost/benefit vs. simple heuristics |
| 1.5 | **Raise/fold strategy:** river decision (near-exact), flop decision (rollouts), preflop 4× decision (rollouts / learned model) | C, M reviews | Strategy tables + EV of each decision point |
| 1.6 | **EXP: House edge & element of risk** under near-optimal play, with 95% CIs | C | Both numbers reported per `03_Math/README.md` |
| 1.7 | **Stress tests:** ties push vs. lose, raise caps (3×/4×), dealer house ways, payout tweaks | C | Comparison table → candidate rule sets |
| 1.8 | **Gate 1 decision:** pick the rule set to carry forward | M | Decision-log entries D-006+ |

Reference point (for calibration only): established poker-based table games typically run a house edge of a few percent of the base wager, with a lower element of risk because of the raises. A result far above that will feel bad to players; far below (or negative) is a non-starter.

Watch-outs the math must answer: (a) how often Hold'em ties because both hands play the board; (b) whether the 4× preflop raise plus six-card information gives skilled players an edge; (c) push frequency (too many pushes = boring and slow revenue).

## Phase 2 — Private playtests (Weeks 3–8, parallel with Phase 1)
| # | Task | Owner | Done when |
|---|---|---|---|
| 2.1 | Print a one-page rules sheet + paper layout (6 spots) | C drafts, M prints | In `05_Layout_Ops/` |
| 2.2 | Optional: private digital prototype to play hands solo or with testers (not public) | C | Playable link, kept private |
| 2.3 | Run 3+ sessions with trusted friends under NDA; you deal | M | `PT-001…003` logs filled from template |
| 2.4 | Measure: time to set the split, hands/hour, confusion points, fun, reaction to pushes and ties | M logs, C analyzes | Playtest summary |
| 2.5 | **Gate 2 decision:** keep, simplify, or change mechanics | M | Decision-log entries |

## Phase 3 — Rules v0.2 + final dealer house way (Weeks 6–9)
| # | Task | Owner | Done when |
|---|---|---|---|
| 3.1 | Design an equity-based, published, deterministic dealer house way; compare against v0.1 by simulation | C | EXP report + house-way document |
| 3.2 | Write `UTO_Rules_v0.2.md` incorporating Gate 1 & 2 decisions; changelog; tag `rules-v0.2` | C, M approves | Tagged in git |
| 3.3 | Re-run house edge on final rules | C | Final math report draft |

## Phase 4 — IP protection (Weeks 8–12)
Not legal advice — this is the checklist to take to a patent attorney.
| # | Task | Owner | Done when |
|---|---|---|---|
| 4.1 | Deeper prior-art search; write a "how UTO differs" summary | C drafts, M reviews | `06_Prior_Art/Novelty_Summary.md` |
| 4.2 | Get quotes/consultations from patent attorneys experienced with casino games; ask about student or low-cost options | M | Notes in `00_Admin/` |
| 4.3 | Decide: file a provisional patent application before any wider exposure | M | Decision logged; filing date recorded |
| 4.4 | Trademark check on the game name (working title only so far) | M | Note in `IP_Checklist.md` |

## Phase 5 — Operational v0.3 (Weeks 10–16)
| # | Task | Owner | Done when |
|---|---|---|---|
| 5.1 | Table layout / felt design (image file) | C drafts, M approves | `.png` in `05_Layout_Ops/` |
| 5.2 | Dealer procedures: deal order, burns, lock-in, settlement order, misdeal handling | C drafts | Procedures doc |
| 5.3 | Rack card (player-facing rules) | C drafts | Rack card file |
| 5.4 | Timed dealing tests with someone with dealer experience, if possible | M | PT logs with hands/hour |

## Phase 6 — Commercial path (Month 4+)
Two routes; decide at Gate 4:
- **License to a table-game distributor** (most common): pitch with patent-pending status, math report and playtest data; the distributor handles certification, approvals and placement; you take a royalty.
- **Go yourself:** pay for independent math certification by a testing lab or game mathematician, find a casino willing to host a trial, submit to regulators (Nevada: form GL-03, deposit of at least $4,000, field trial of typically 45–180 days at the regulator's discretion). See `07_Submission/Submission_Checklist.md`.

| # | Task | Owner |
|---|---|---|
| 6.1 | Build a short pitch pack (one-pager, math summary, playtest stats, demo) | C drafts, M |
| 6.2 | Research distributors and their submission processes | C researches |
| 6.3 | Choose route (Gate 4) and log the decision | M |

---

## This week (starting 2026-10-26)
- [ ] **M:** Fill in conception date (0.1); read the Aprende agreement (0.2).
- [ ] **C:** Build the hand evaluator + tests (1.1) and game engine (1.2); commit and push.
- [ ] **C:** Run EXP-001 baseline (1.3) and report the first numbers.
- [ ] **C:** Draft the playtest NDA template (0.4).
