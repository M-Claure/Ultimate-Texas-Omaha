# Invention Log
Dated, append-only record of how the game was conceived and developed. Write entries the day things happen. Don't edit old entries — add a correction entry instead.

Tip: periodically export this file to PDF and email it to yourself (or store it somewhere with independent timestamps) so there is third-party evidence of the date.

**Entry template**
```
## YYYY-MM-DD — <title>
- What was conceived / changed:
- Who was involved:
- Files created/updated:
- Who it was disclosed to (also log in Disclosure_Log.md):
```

---

## [2026-10-21] — Original concept
- What was conceived: Six-card Hold'em/Omaha split game vs dealer, Pai Gow-style aggregate settlement, UTH-style staged raises.
- Who was involved: [FILL IN — anyone who helped shape the idea, including AI tools used]
- Files: `01_Rules/archive/Ultimate_Texas_Omaha_Concept.docx` (note: this file's internal metadata dates are template defaults and are NOT a reliable record of when it was written)

## 2026-10-21 — Project record established
- What changed: Created folder structure and documentation system. Converted concept draft into formal Rules v0.1 (no substantive rule changes). Logged decisions D-001–D-005.
- Who was involved: Matias, with Claude (AI assistant) for documentation.
- Files created: README.md, 01_Rules/UTO_Rules_v0.1.md, 01_Rules/CHANGELOG.md, 02_Decisions/Decision_Log.md, admin/math/playtest/prior-art/submission templates.
- Disclosed to: none new.

## 2026-10-21 — Development roadmap created
- What changed: Added ROADMAP.md: phases from housekeeping/IP hygiene through math v0.2, playtests, rules v0.2, IP protection, operations and commercial path, with gates and owners.
- Who was involved: Matias, with Claude (AI assistant).
- Disclosed to: none new.

## 2026-10-21 — Tie rule clarified (Rules v0.2)
- What changed: Matias clarified that a tie counts as a lost hand, not an automatic overall loss (Win+Tie = push). Recorded as D-006, Rules v0.2.
- Who was involved: Matias, with Claude (AI assistant).
- Disclosed to: none new.

## 2026-10-21 — Math engine built; EXP-001 dealer split tournament
- What changed: Built hand evaluator, equity tables, house-way rules and simulator (03_Math/src). EXP-001 compared dealer split rules; weighted rule C (w=0.5) is best. Found that under Rules v0.2 payouts a simple player strategy beats the house by ~17% of Base, so the betting/payout structure must be rebalanced.
- Who was involved: Matias, with Claude (AI assistant).
- Disclosed to: none new.

## 2026-10-21 — Dealer-friendly House Way H; payout structure scan (EXP-002)
- What changed: Matias rejected the equity-based dealer rule (needs to be dealer-usable). Derived House Way H (5-step rank rule) from the best computed rule. Scanned 40 payout/raise structures; making the Base push on a win (keeping 4x/2x/1x) gives ~2% house edge.
- Who was involved: Matias, with Claude (AI assistant).
- Disclosed to: none new.
