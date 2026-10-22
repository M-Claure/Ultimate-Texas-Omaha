"""Optimal player strategy by backward induction (Monte Carlo over unseen cards).

For one player 6-card hand the engine samples M flops; for each flop K turn/river completions;
for each full board D dealer hands (dealer splits with the house way). From these it estimates,
for every one of the player's 15 splits and every sampled board, P(player wins both hands) = pw
and P(player wins neither) = pl. The optimal policy is then solved backwards for any payout
structure:

  river (only if no raise yet):  call R3  vs  fold         value Vr(B) = max(A_R3(B), -1)
  flop  (only if no raise yet):  raise R2 vs check         Vf(F) = max(mean_B A_R2, mean_B Vr)
  preflop:                       raise R1 vs check         V     = max(mean A_R1, mean_F Vf)
  split: the split with the highest V.
where A_R(B) = R*(pw - pl) + bw*pw - pl   (Play bet R pays 1:1; Base pays bw on a win,
                                            pushes on a push, loses on a loss)

Using the same samples for every split/action (common random numbers) makes comparisons precise.
Because decisions and values use the same samples, each max() is slightly optimistic for the
player (house edge slightly understated); precision is checked by re-running with more samples.

Structures: rows of [R1, R2, R3, bw, fold_allowed].
"""
import numpy as np
from numba import njit, prange
from .evaluator import eval_cards, omaha_pair, holdem_fast
from .equity import idx2
from .house_way import PAIRS6, COMP6, COMP_PAIRS, choose_split

# per-structure output columns
OUT_COLS = ["ev", "split", "pre_raise", "p_flop_raise", "p_call", "p_fold",
            "w4", "p4", "l4", "w2", "p2", "l2", "w1", "p1", "l1", "e_bet", "e_res2",
            "ev_raise_pre", "ev_check_pre"]
NO = len(OUT_COLS)


@njit(cache=False)
def _board_counts(rest, D, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, he_p, om_p, win, loss):
    """rest[0:5] is the board, rest[5:46] the 41 unseen cards. Fills win/loss counts per split
    (15) over D sampled dealer hands. he_p/om_p: player's 15 pair values on this board."""
    board = rest[0:5]
    # dealer pair values for every pair of the 41 unseen cards
    heP = np.zeros(1326, np.int64)
    omP = np.zeros(1326, np.int64)
    cs = np.empty(7, np.int64)
    for k in range(5):
        cs[2 + k] = board[k]
    for i in range(5, 46):
        for j in range(i + 1, 46):
            a = rest[i]
            b = rest[j]
            cs[0] = a
            cs[1] = b
            ix = idx2(a, b)
            heP[ix] = eval_cards(cs, 7)
            omP[ix] = omaha_pair(a, b, board, NF, FL)
    # player split values
    pHE = np.empty(15, np.int64)
    pOM = np.empty(15, np.int64)
    for s in range(15):
        pHE[s] = he_p[s]
        best = 0
        for m in range(6):
            v = om_p[COMP_PAIRS[s, m]]
            if v > best:
                best = v
        pOM[s] = best
    dh = np.empty(6, np.int64)
    for s in range(15):
        win[s] = 0
        loss[s] = 0
    for _ in range(D):
        for k in range(6):
            r = 5 + k + np.random.randint(41 - k)
            rest[5 + k], rest[r] = rest[r], rest[5 + k]
        for k in range(6):
            dh[k] = rest[5 + k]
        dp = choose_split(dh, d_rule, d_w, True, HEW, HET, OMW, OMT)
        dHE = heP[idx2(dh[PAIRS6[dp, 0]], dh[PAIRS6[dp, 1]])]
        dOM = 0
        for m in range(6):
            q = COMP_PAIRS[dp, m]
            v = omP[idx2(dh[PAIRS6[q, 0]], dh[PAIRS6[q, 1]])]
            if v > dOM:
                dOM = v
        for s in range(15):
            w = (1 if pHE[s] > dHE else 0) + (1 if pOM[s] > dOM else 0)
            if w == 2:
                win[s] += 1
            elif w == 0:
                loss[s] += 1


@njit(cache=False)
def _A(R, bw, pw, pl):
    return R * (pw - pl) + bw * pw - pl


@njit(cache=False)
def solve_hand(ph, M, K, D, d_rule, d_w, ST, HEW, HET, OMW, OMT, NF, FL, out, splitv, bracket):
    """Fill out[S, NO] (in-sample optimal policy statistics), splitv[S, 15] (in-sample value of
    each split) and bracket[S, 2] = (in-sample EV, cross-fitted EV) for one player hand.

    Cross-fitting: every decision (river call/fold, flop raise/check, split + preflop action) is
    made on one half of the samples and scored on the other half (both ways, averaged). That is
    an unbiased estimate of a strategy the player could actually follow, so its EV is a LOWER
    bound on optimal-play EV, while the in-sample EV is (in expectation) an UPPER bound."""
    rest = np.empty(46, np.int64)
    j = 0
    for c in range(52):
        hit = False
        for k in range(6):
            if ph[k] == c:
                hit = True
        if not hit:
            rest[j] = c
            j += 1
    Dh = D // 2
    PW = np.zeros((15, M, K, 2))
    PL = np.zeros((15, M, K, 2))
    win = np.zeros(15, np.int64)
    loss = np.zeros(15, np.int64)
    he_p = np.empty(15, np.int64)
    om_p = np.empty(15, np.int64)
    for m in range(M):
        for k in range(3):
            r = k + np.random.randint(46 - k)
            rest[k], rest[r] = rest[r], rest[k]
        for kk in range(K):
            for k in range(3, 5):
                r = k + np.random.randint(46 - k)
                rest[k], rest[r] = rest[r], rest[k]
            board = rest[0:5]
            for p in range(15):
                a = ph[PAIRS6[p, 0]]
                b = ph[PAIRS6[p, 1]]
                he_p[p] = holdem_fast(a, b, board, NF, FL)
                om_p[p] = omaha_pair(a, b, board, NF, FL)
            for h in range(2):
                _board_counts(rest, Dh, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, he_p, om_p, win, loss)
                for s in range(15):
                    PW[s, m, kk, h] = win[s] / Dh
                    PL[s, m, kk, h] = loss[s] / Dh
    S = ST.shape[0]
    VrI = np.zeros((M, K))
    VrP = np.zeros((M, K))
    A2 = np.zeros((M, K))
    A1 = np.zeros((M, K))
    VfI = np.zeros(M)
    VfP = np.zeros(M)
    VfI_half = np.zeros((M, 2))   # in-sample flop value using only board half h (for decisions)
    for si in range(S):
        R1 = ST[si, 0]
        R2 = ST[si, 1]
        R3 = ST[si, 2]
        bw = ST[si, 3]
        fold_ok = ST[si, 4] > 0.5
        bestI = -1e9
        bests = 0
        # cross-fit candidates per flop-half: best (split, action) chosen on half a
        cand_v = np.full(2, -1e9)
        cand_s = np.zeros(2, np.int64)
        cand_a = np.zeros(2, np.int64)
        # store per split the half-specific values needed for scoring
        rawH = np.zeros((15, 2))   # mean A1 over flops in half h
        chkH = np.zeros((15, 2))   # mean VfP over flops in half h (pessimistic, for scoring)
        chkHI = np.zeros((15, 2))  # mean VfI over flops in half h (for deciding)
        for s in range(15):
            for m in range(M):
                for kk in range(K):
                    pw0 = PW[s, m, kk, 0]
                    pl0 = PL[s, m, kk, 0]
                    pw1 = PW[s, m, kk, 1]
                    pl1 = PL[s, m, kk, 1]
                    pw = 0.5 * (pw0 + pw1)
                    pl = 0.5 * (pl0 + pl1)
                    A1[m, kk] = _A(R1, bw, pw, pl)
                    A2[m, kk] = _A(R2, bw, pw, pl)
                    a3 = _A(R3, bw, pw, pl)
                    a30 = _A(R3, bw, pw0, pl0)
                    a31 = _A(R3, bw, pw1, pl1)
                    if fold_ok:
                        VrI[m, kk] = a3 if a3 > -1.0 else -1.0
                        # decide on one dealer half, score on the other
                        v = 0.0
                        v += a31 if a30 > -1.0 else -1.0
                        v += a30 if a31 > -1.0 else -1.0
                        VrP[m, kk] = 0.5 * v
                    else:
                        VrI[m, kk] = a3
                        VrP[m, kk] = a3
                # flop decisions
                r2 = 0.0
                ck = 0.0
                r2h = np.zeros(2)
                ckh = np.zeros(2)
                ckPh = np.zeros(2)
                cnt = np.zeros(2)
                for kk in range(K):
                    h = kk & 1
                    r2 += A2[m, kk]
                    ck += VrI[m, kk]
                    r2h[h] += A2[m, kk]
                    ckh[h] += VrI[m, kk]
                    ckPh[h] += VrP[m, kk]
                    cnt[h] += 1
                r2 /= K
                ck /= K
                VfI[m] = r2 if (R2 > 0 and r2 > ck) else ck
                v = 0.0
                for h in range(2):
                    o_ = 1 - h
                    dec_raise = R2 > 0 and (r2h[h] / cnt[h]) > (ckh[h] / cnt[h])
                    v += (r2h[o_] / cnt[o_]) if dec_raise else (ckPh[o_] / cnt[o_])
                VfP[m] = 0.5 * v
            raise_pre = 0.0
            check_pre = 0.0
            for m in range(M):
                for kk in range(K):
                    raise_pre += A1[m, kk]
                check_pre += VfI[m]
                h = m & 1
                a1m = 0.0
                for kk in range(K):
                    a1m += A1[m, kk]
                rawH[s, h] += a1m / K
                chkH[s, h] += VfP[m]
                chkHI[s, h] += VfI[m]
            raise_pre /= (M * K)
            check_pre /= M
            v = raise_pre if raise_pre > check_pre else check_pre
            splitv[si, s] = v
            if v > bestI:
                bestI = v
                bests = s
            for h in range(2):
                nh = (M + 1 - h) // 2
                if rawH[s, h] / nh > cand_v[h]:
                    cand_v[h] = rawH[s, h] / nh
                    cand_s[h] = s
                    cand_a[h] = 1
                if chkHI[s, h] / nh > cand_v[h]:
                    cand_v[h] = chkHI[s, h] / nh
                    cand_s[h] = s
                    cand_a[h] = 0
        # cross-fitted EV: decide on flop half h, score on the other half
        vP = 0.0
        for h in range(2):
            o_ = 1 - h
            no = (M + 1 - o_) // 2
            s_ = cand_s[h]
            vP += (rawH[s_, o_] / no) if cand_a[h] == 1 else (chkH[s_, o_] / no)
        bracket[si, 0] = bestI
        bracket[si, 1] = 0.5 * vP
        # ---- statistics of the in-sample optimal policy for the chosen split ----
        s = bests
        o = out[si]
        for c in range(NO):
            o[c] = 0.0
        o[0] = bestI
        o[1] = s
        raise_pre = 0.0
        check_pre = 0.0
        flop_raise = np.zeros(M, np.bool_)
        for m in range(M):
            r2 = 0.0
            ck = 0.0
            for kk in range(K):
                pw = 0.5 * (PW[s, m, kk, 0] + PW[s, m, kk, 1])
                pl = 0.5 * (PL[s, m, kk, 0] + PL[s, m, kk, 1])
                raise_pre += _A(R1, bw, pw, pl)
                r2 += _A(R2, bw, pw, pl)
                a3 = _A(R3, bw, pw, pl)
                if fold_ok and a3 < -1.0:
                    a3 = -1.0
                ck += a3
            flop_raise[m] = R2 > 0 and r2 > ck
            check_pre += (r2 if flop_raise[m] else ck) / K
        raise_pre /= (M * K)
        check_pre /= M
        o[17] = raise_pre
        o[18] = check_pre
        wgt = 1.0 / (M * K)
        if raise_pre > check_pre:
            o[2] = 1.0
            o[15] = 1.0 + R1
        else:
            for m in range(M):
                if flop_raise[m]:
                    o[3] += 1.0 / M
        for m in range(M):
            for kk in range(K):
                pw = 0.5 * (PW[s, m, kk, 0] + PW[s, m, kk, 1])
                pl = 0.5 * (PL[s, m, kk, 0] + PL[s, m, kk, 1])
                pu = 1.0 - pw - pl
                if o[2] > 0.5:
                    o[6] += wgt * pw
                    o[7] += wgt * pu
                    o[8] += wgt * pl
                    o[16] += wgt * (pw * (bw + R1) ** 2 + pl * (1 + R1) ** 2)
                elif flop_raise[m]:
                    o[9] += wgt * pw
                    o[10] += wgt * pu
                    o[11] += wgt * pl
                    o[16] += wgt * (pw * (bw + R2) ** 2 + pl * (1 + R2) ** 2)
                    o[15] += wgt * (1.0 + R2)
                else:
                    a3 = _A(R3, bw, pw, pl)
                    if fold_ok and a3 < -1.0:
                        o[5] += wgt
                        o[16] += wgt
                        o[15] += wgt
                    else:
                        o[4] += wgt
                        o[12] += wgt * pw
                        o[13] += wgt * pu
                        o[14] += wgt * pl
                        o[16] += wgt * (pw * (bw + R3) ** 2 + pl * (1 + R3) ** 2)
                        o[15] += wgt * (1.0 + R3)


@njit(parallel=True)
def solve_many(n, seed, M, K, D, d_rule, d_w, ST, HEW, HET, OMW, OMT, NF, FL):
    S = ST.shape[0]
    OUT = np.zeros((n, S, NO))
    SV = np.zeros((n, S, 15))
    BR = np.zeros((n, S, 2))
    HANDS = np.zeros((n, 6), np.int64)
    for i in prange(n):
        np.random.seed(seed + i)
        deck = np.arange(52)
        for k in range(6):
            r = k + np.random.randint(52 - k)
            deck[k], deck[r] = deck[r], deck[k]
        ph = deck[0:6].copy()
        HANDS[i] = ph
        solve_hand(ph, M, K, D, d_rule, d_w, ST, HEW, HET, OMW, OMT, NF, FL, OUT[i], SV[i], BR[i])
    return HANDS, OUT, SV, BR
