# Math & Simulation
Goal (v0.2): exact evaluators, simulator, optimal raise/fold policy, house edge and element of risk for each rules version.

## Rules for this folder
- Code lives in `src/` (create when work starts). Put this folder under git so every result can point to a commit.
- Each experiment gets a file in `experiments/` named `EXP-###_<short-name>.md`, using the template below, and a row in `Results_Index.md`.
- Every experiment records: rules version, code commit, random seed, number of hands, and confidence intervals (not just point estimates).
- Report **both**: house edge = −EV / Base, and element of risk = −EV / average total wagered.

## Planned work (from concept draft)
1. Five-card evaluator incl. Omaha exactly-two rule; unit tests for ties, straights, flushes, board-only Hold'em.
2. Enumerate 15 player splits + dealer house way; deal without replacement.
3. Optimal policies for preflop 4×, flop 2×, river 1×/fold via conditional EV (random-play simulation is not enough).
4. Win/push/loss probabilities by action; house edge; volatility; hands per hour.
5. Stress tests: raise caps, fold timing, tie treatment, house ways, payouts.

## Experiment template
```
# EXP-### — <title>
- Date:
- Rules version tested:
- Question:
- Method:
- Code commit / script:
- Seed(s), hands simulated:
- Results (with 95% CIs):
- Conclusion:
- Leads to decision: D-### (if any)
```
