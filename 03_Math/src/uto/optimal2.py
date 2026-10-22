"""Optimal-play engine v2: same backward induction as optimal.py, with variance reduction.

Value of a split s for a structure (R1, R2, R3, bw, fold):
  A_R(pw, pl) = R*(pw - pl) + bw*pw - pl                          (EV of finishing with Play bet R)
  fold gain at a river board   g(B)  = max(0, -1 - A_R3(B))       (0 if fold not allowed)
  flop increment               d(F)  = (R2 - R3) * E[pw - pl | F]
  V_raise_pre = E[A_R1] = E[A_R3] + (R1 - R3) * E[pw - pl]
  V_check_pre = E[A_R3] + E_F[ max( d(F), E[g | F] ) ]
  V(s)        = max(V_raise_pre, V_check_pre); the player takes the split with the highest V.

The "linear" terms E[pw], E[pl] are estimated from many cheap joint samples (fresh board +
dealer hands), so only the small option values (flop raise / river fold) carry nested-sampling
noise. Flop conditional means use K boards x D dealers plus NF extra joint samples per flop.

Two estimates per hand (bracket): in-sample (decisions and values from the same samples ->
optimistic for the player) and cross-fitted (each decision made on one half of the samples and
scored on the other -> a strategy the player could really follow -> pessimistic).
"""
import numpy as np
from numba import njit, prange
from .evaluator import eval_cards, omaha_pair, holdem_fast
from .equity import idx2
from .house_way import PAIRS6, COMP6, COMP_PAIRS, choose_split
from .optimal import _board_counts

NO2 = 21
OUT2_COLS = ["ev_in", "ev_cross", "split", "pre_raise", "p_flop_raise", "p_fold",
             "e_bet", "p_win", "p_loss", "e_res2", "v_raise_pre", "v_check_pre",
             "w4", "p4", "l4", "w2", "p2", "l2", "w1", "p1", "l1"]


@njit(cache=False)
def _player_vals(ph, board, NF, FL, pHE, pOM, he_p, om_p):
    for p in range(15):
        a = ph[PAIRS6[p, 0]]
        b = ph[PAIRS6[p, 1]]
        he_p[p] = holdem_fast(a, b, board, NF, FL)
        om_p[p] = omaha_pair(a, b, board, NF, FL)
    for s in range(15):
        pHE[s] = he_p[s]
        best = 0
        for m in range(6):
            v = om_p[COMP_PAIRS[s, m]]
            if v > best:
                best = v
        pOM[s] = best


@njit(cache=False)
def _dealer_vals(dh, board, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL):
    dp = choose_split(dh, d_rule, d_w, True, HEW, HET, OMW, OMT)
    dHE = holdem_fast(dh[PAIRS6[dp, 0]], dh[PAIRS6[dp, 1]], board, NF, FL)
    dOM = 0
    for m in range(6):
        q = COMP_PAIRS[dp, m]
        v = omaha_pair(dh[PAIRS6[q, 0]], dh[PAIRS6[q, 1]], board, NF, FL)
        if v > dOM:
            dOM = v
    return dHE, dOM


@njit(cache=False)
def _joint(rest, nfix, nboards, ndealers, ph, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, W, L):
    """Joint samples: rest[0:nfix] board cards already fixed; complete the board nboards times,
    ndealers dealer hands per board. Accumulates per-split win/loss counts into W, L.
    Returns number of samples."""
    pHE = np.empty(15, np.int64)
    pOM = np.empty(15, np.int64)
    he_p = np.empty(15, np.int64)
    om_p = np.empty(15, np.int64)
    dh = np.empty(6, np.int64)
    n = 0
    for _ in range(nboards):
        for k in range(nfix, 5):
            r = k + np.random.randint(46 - k)
            rest[k], rest[r] = rest[r], rest[k]
        board = rest[0:5]
        _player_vals(ph, board, NF, FL, pHE, pOM, he_p, om_p)
        for _d in range(ndealers):
            for k in range(6):
                r = 5 + k + np.random.randint(41 - k)
                rest[5 + k], rest[r] = rest[r], rest[5 + k]
            for k in range(6):
                dh[k] = rest[5 + k]
            dHE, dOM = _dealer_vals(dh, board, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL)
            for s in range(15):
                w = (1 if pHE[s] > dHE else 0) + (1 if pOM[s] > dOM else 0)
                if w == 2:
                    W[s] += 1
                elif w == 0:
                    L[s] += 1
            n += 1
    return n


@njit(cache=False)
def solve_hand2(ph, NLB, NLD, M, K, D, NFB, ST, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, out, splitv):
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
    # ---- linear stage: unconditional E[pw], E[pl] per split, two independent halves ----
    LW = np.zeros((2, 15))
    LL = np.zeros((2, 15))
    for h in range(2):
        W = np.zeros(15, np.int64)
        L = np.zeros(15, np.int64)
        n = _joint(rest, 0, NLB // 2, NLD, ph, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, W, L)
        for s in range(15):
            LW[h, s] = W[s] / n
            LL[h, s] = L[s] / n
    # ---- nested stage ----
    Dh = D // 2
    PW = np.zeros((15, M, K, 2))
    PL = np.zeros((15, M, K, 2))
    FW = np.zeros((15, M, 2))     # flop conditional P(win) from extra joint samples, halves
    FLs = np.zeros((15, M, 2))
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
        for h in range(2):
            W = np.zeros(15, np.int64)
            L = np.zeros(15, np.int64)
            n = _joint(rest, 3, NFB // 2, 2, ph, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, W, L)
            for s in range(15):
                FW[s, m, h] = W[s] / n
                FLs[s, m, h] = L[s] / n
    # ---- solve each structure ----
    S = ST.shape[0]
    wB = K / (K + NFB / 2.0)     # weight of board-based vs joint-sample flop means (effective boards)
    for si in range(S):
        R1 = ST[si, 0]
        R2 = ST[si, 1]
        R3 = ST[si, 2]
        bw = ST[si, 3]
        fold_ok = ST[si, 4] > 0.5
        bestI = -1e9
        bests = 0
        bestRaise = False
        bestVR = 0.0
        bestVC = 0.0
        # cross-fit: decision data half h, scoring half 1-h (for linear terms, flop halves via m parity,
        # river via dealer halves)
        candv = np.full(2, -1e9)
        cands = np.zeros(2, np.int64)
        canda = np.zeros(2, np.int64)
        scoreR = np.zeros((15, 2))   # raise-pre value scored with half h data
        scoreC = np.zeros((15, 2))   # check-pre value scored with half h data (decisions from other half)
        decR = np.zeros((15, 2))
        decC = np.zeros((15, 2))
        for s in range(15):
            ew = 0.5 * (LW[0, s] + LW[1, s])
            el = 0.5 * (LL[0, s] + LL[1, s])
            lin3 = R3 * (ew - el) + bw * ew - el
            vR = lin3 + (R1 - R3) * (ew - el)
            opt = 0.0
            # per-half option sums for cross-fit
            optD = np.zeros(2)   # decision estimate on half h (flops of parity h)
            optS = np.zeros(2)   # pessimistic scored value on half h
            cnt = np.zeros(2)
            for m in range(M):
                # flop conditional mean of (pw - pl): boards (both dealer halves) + extra joint samples
                sb = 0.0
                for kk in range(K):
                    sb += 0.5 * (PW[s, m, kk, 0] + PW[s, m, kk, 1] - PL[s, m, kk, 0] - PL[s, m, kk, 1])
                sj = 0.5 * (FW[s, m, 0] + FW[s, m, 1] - FLs[s, m, 0] - FLs[s, m, 1])
                dF = (R2 - R3) * (wB * (sb / K) + (1.0 - wB) * sj)
                g = 0.0
                if fold_ok:
                    for kk in range(K):
                        pw = 0.5 * (PW[s, m, kk, 0] + PW[s, m, kk, 1])
                        pl = 0.5 * (PL[s, m, kk, 0] + PL[s, m, kk, 1])
                        a3 = R3 * (pw - pl) + bw * pw - pl
                        if a3 < -1.0:
                            g += -1.0 - a3
                    g /= K
                if R2 > 0 and dF > g:
                    opt += dF
                else:
                    opt += g
                # ---- pessimistic flop value: decide with one data half, score with the other ----
                # halves: board parity for boards, joint-half for joint samples, dealer half for river
                h_m = m & 1
                vS = 0.0
                for hd in range(2):
                    ho = 1 - hd
                    sbd = 0.0
                    sbo = 0.0
                    nd = 0
                    no = 0
                    gd = 0.0
                    go = 0.0
                    for kk in range(K):
                        x = PW[s, m, kk, hd] - PL[s, m, kk, hd]
                        y = PW[s, m, kk, ho] - PL[s, m, kk, ho]
                        if (kk & 1) == hd:
                            sbd += x
                            nd += 1
                            if fold_ok:
                                a3 = R3 * (PW[s, m, kk, hd] - PL[s, m, kk, hd]) + bw * PW[s, m, kk, hd] - PL[s, m, kk, hd]
                                if a3 < -1.0:
                                    gd += -1.0 - a3
                        else:
                            sbo += y
                            no += 1
                            if fold_ok:
                                # river decided on dealer half hd, scored on half ho
                                a3d = R3 * (PW[s, m, kk, hd] - PL[s, m, kk, hd]) + bw * PW[s, m, kk, hd] - PL[s, m, kk, hd]
                                a3o = R3 * (PW[s, m, kk, ho] - PL[s, m, kk, ho]) + bw * PW[s, m, kk, ho] - PL[s, m, kk, ho]
                                if a3d < -1.0:
                                    go += -1.0 - a3o
                    dD = (R2 - R3) * (wB * (sbd / max(nd, 1)) + (1.0 - wB) * (FW[s, m, hd] - FLs[s, m, hd]))
                    dO = (R2 - R3) * (wB * (sbo / max(no, 1)) + (1.0 - wB) * (FW[s, m, ho] - FLs[s, m, ho]))
                    gD = gd / max(nd, 1)
                    gO = go / max(no, 1)
                    if R2 > 0 and dD > gD:
                        vS += dO
                    else:
                        vS += gO
                    if hd == 0:
                        dec_here = dD if (R2 > 0 and dD > gD) else gD
                optD[h_m] += (dF if (R2 > 0 and dF > g) else g)
                optS[h_m] += 0.5 * vS
                cnt[h_m] += 1
            opt /= M
            vC = lin3 + opt
            v = vR if vR > vC else vC
            splitv[si, s, 0] = v
            splitv[si, s, 1] = vR
            splitv[si, s, 2] = vC
            if v > bestI:
                bestI = v
                bests = s
                bestRaise = vR > vC
                bestVR = vR
                bestVC = vC
            # cross-fit pieces: decision on half h uses linear half h + flop option decision estimates of
            # flops with parity h; scoring on half 1-h uses linear half 1-h + pessimistic option values of
            # flops with parity 1-h
            for h in range(2):
                ewh = LW[h, s]
                elh = LL[h, s]
                l3h = R3 * (ewh - elh) + bw * ewh - elh
                decR[s, h] = l3h + (R1 - R3) * (ewh - elh)
                decC[s, h] = l3h + optD[h] / max(cnt[h], 1)
                scoreR[s, h] = decR[s, h]
                scoreC[s, h] = l3h + optS[h] / max(cnt[h], 1)
        vP = 0.0
        for h in range(2):
            o_ = 1 - h
            bv = -1e9
            bs = 0
            ba = 0
            for s in range(15):
                if decR[s, h] > bv:
                    bv = decR[s, h]
                    bs = s
                    ba = 1
                if decC[s, h] > bv:
                    bv = decC[s, h]
                    bs = s
                    ba = 0
            vP += scoreR[bs, o_] if ba == 1 else scoreC[bs, o_]
        o = out[si]
        o[0] = bestI
        o[1] = 0.5 * vP
        o[2] = bests
        o[3] = 1.0 if bestRaise else 0.0
        # policy statistics for the chosen split (in-sample)
        s = bests
        ew = 0.5 * (LW[0, s] + LW[1, s])
        el = 0.5 * (LL[0, s] + LL[1, s])
        o[10] = bestVR
        o[11] = bestVC
        for c in range(12, NO2):
            o[c] = 0.0
        if bestRaise:
            o[6] = 1.0 + R1
            o[7] = ew
            o[8] = el
            o[9] = ew * (bw + R1) ** 2 + el * (1 + R1) ** 2
            o[12] = ew
            o[14] = el
            o[13] = 1.0 - ew - el
        else:
            pfr = 0.0
            pf = 0.0
            eb = 0.0
            pwin = 0.0
            plos = 0.0
            er2 = 0.0
            for m in range(M):
                sb = 0.0
                for kk in range(K):
                    sb += 0.5 * (PW[s, m, kk, 0] + PW[s, m, kk, 1] - PL[s, m, kk, 0] - PL[s, m, kk, 1])
                sj = 0.5 * (FW[s, m, 0] + FW[s, m, 1] - FLs[s, m, 0] - FLs[s, m, 1])
                dF = (R2 - R3) * (wB * (sb / K) + (1.0 - wB) * sj)
                g = 0.0
                for kk in range(K):
                    pw = 0.5 * (PW[s, m, kk, 0] + PW[s, m, kk, 1])
                    pl = 0.5 * (PL[s, m, kk, 0] + PL[s, m, kk, 1])
                    a3 = R3 * (pw - pl) + bw * pw - pl
                    if fold_ok and a3 < -1.0:
                        g += -1.0 - a3
                g /= K
                raise2 = R2 > 0 and dF > g
                if raise2:
                    pfr += 1.0
                for kk in range(K):
                    pw = 0.5 * (PW[s, m, kk, 0] + PW[s, m, kk, 1])
                    pl = 0.5 * (PL[s, m, kk, 0] + PL[s, m, kk, 1])
                    if raise2:
                        eb += 1.0 + R2
                        pwin += pw
                        plos += pl
                        o[15] += pw / (M * K)
                        o[17] += pl / (M * K)
                        o[16] += (1.0 - pw - pl) / (M * K)
                        er2 += pw * (bw + R2) ** 2 + pl * (1 + R2) ** 2
                    else:
                        a3 = R3 * (pw - pl) + bw * pw - pl
                        if fold_ok and a3 < -1.0:
                            pf += 1.0
                            eb += 1.0
                            plos += 1.0
                            er2 += 1.0
                        else:
                            eb += 1.0 + R3
                            pwin += pw
                            plos += pl
                            o[18] += pw / (M * K)
                            o[20] += pl / (M * K)
                            o[19] += (1.0 - pw - pl) / (M * K)
                            er2 += pw * (bw + R3) ** 2 + pl * (1 + R3) ** 2
            o[4] = pfr / M
            o[5] = pf / (M * K)
            o[6] = eb / (M * K)
            o[7] = pwin / (M * K)
            o[8] = plos / (M * K)
            o[9] = er2 / (M * K)


@njit(parallel=True)
def solve_many2(n, seed, NLB, NLD, M, K, D, NFB, ST, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL):
    S = ST.shape[0]
    OUT = np.zeros((n, S, NO2))
    SV = np.zeros((n, S, 15, 3))
    HANDS = np.zeros((n, 6), np.int64)
    for i in prange(n):
        np.random.seed(seed + i)
        deck = np.arange(52)
        for k in range(6):
            r = k + np.random.randint(52 - k)
            deck[k], deck[r] = deck[r], deck[k]
        ph = deck[0:6].copy()
        HANDS[i] = ph
        solve_hand2(ph, NLB, NLD, M, K, D, NFB, ST, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, OUT[i], SV[i])
    return HANDS, OUT, SV


@njit(parallel=True)
def solve_given2(HANDS, seed, NLB, NLD, M, K, D, NFB, ST, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL):
    """Same as solve_many2 but for given player hands (MC seeded by seed + i)."""
    n = HANDS.shape[0]
    S = ST.shape[0]
    OUT = np.zeros((n, S, NO2))
    SV = np.zeros((n, S, 15, 3))
    for i in prange(n):
        np.random.seed(seed + i)
        solve_hand2(HANDS[i].copy(), NLB, NLD, M, K, D, NFB, ST, d_rule, d_w, HEW, HET, OMW, OMT, NF, FL, OUT[i], SV[i])
    return OUT, SV
