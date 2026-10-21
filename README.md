# Ultimate Texas Omaha (UTO) — Project Record

Working title only. Owner/inventor: Matias.
This folder is the single source of truth for the design, math, testing, IP and regulatory record of UTO.

## Current status
| Item | Value |
|---|---|
| Current rules version | **v0.1** (`01_Rules/UTO_Rules_v0.1.md`) |
| Stage | Prototype — payouts, house edge, strategy and dealer house way unvalidated |
| Next milestone | Math v0.2: evaluator + simulator, optimal raise strategy, house edge |
| Public disclosure so far | See `00_Admin/Disclosure_Log.md` |

## Folder map
| Folder | What goes here |
|---|---|
| `00_Admin/` | Invention log (dated), disclosure/NDA log, IP checklist |
| `01_Rules/` | Versioned rules specs + `CHANGELOG.md`. `archive/` holds superseded/original drafts — never edit them |
| `02_Decisions/` | Decision log: every rule or design choice, with reason and evidence |
| `03_Math/` | Simulation/analysis code and results. Each experiment cites a rules version and random seed |
| `04_Playtests/` | One log per playtest session + index |
| `05_Layout_Ops/` | Felt layout, dealer procedures, house way, rack card |
| `06_Prior_Art/` | Similar games and patents reviewed, and how UTO differs |
| `07_Submission/` | Regulator/lab package: rules, paytables, math report, certification, forms |

## Conventions (the rules that keep the record trustworthy)
1. **Dates:** always ISO `YYYY-MM-DD`.
2. **Rules versions:** never overwrite a rules file. A change = new file (`UTO_Rules_v0.2.md`) + `CHANGELOG.md` entry + decision-log entry. Minor wording fixes bump the patch (`v0.1.1`).
3. **Traceability:** every math result and playtest names the rules version it tested. Every rules change cites the decision (`D-###`) that caused it; every decision cites its evidence (`EXP-###`, `PT-###`, or reasoning).
4. **IDs:** decisions `D-###`, experiments `EXP-###`, playtests `PT-###`, prior-art items `PA-###`, invention-log entries by date.
5. **Append-only logs:** fix mistakes with a new dated entry ("Correction to …"), don't delete history.
6. **Disclosure discipline:** log everyone who sees the rules (`00_Admin/Disclosure_Log.md`). Avoid public posting until IP strategy is settled (see `00_Admin/IP_Checklist.md`).

## Version control
This folder is a git repo (`origin`: github.com/M-Claure/Ultimate-Texas-Omaha). Commit after each meaningful change with a message that cites IDs, e.g. `Rules v0.2: ties push (D-006, EXP-003)`. Tag each rules release (`git tag rules-v0.1`).
