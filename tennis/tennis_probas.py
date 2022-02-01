## given probability of winning a best-of-three-set match and the assumption that sets are independent,
## output the probability of winning a best-of-five-set match

##One way to find the probability of winning an n-set match is to start with the probability of winning
##a single set.  If we have an estimated probability of winning a best-of-three, e.g. from betting odds,
##we need to work backwards to get the probability of winning a single set.
##
##If x is p(set win), the probability of winning a three-setter is:
##    x^2 + 2(x^2)(1-x)
##    x^2 is the p(winning in straight sets)
##    (x^2)(1-x) is the p(winning two sets and losing one)
##    and there are 2 permutations (LWW and WLW) that result in a three-set win
##
##Written another way, we have:
##    p(three-set-win) = -2x^3 + 3x^2
##    or: -2x^3 + 3x^2 - p(three-set-win) = 0
##
##The first line of the function solves the trinomial for the relevant root.
##The second line uses similar logic to generate the probability of winning a five-setter:
##    x^3 --- p(straight-set-win)
##    3(x^3)(1-x) --- p(four-set-win): three sets won, one set lost, three permutations
##    6(x^3)(1-x)(1-x) --- p(five-set-win): two sets lost, six permutations (4c2)

import numpy


def get_one_set_proba(matchproba_bo3: float) -> float:
    """Returns the probability for one set from the proba for the match (best of 3 sets)

    Args:
        matchproba_bo3 (float): [description]

    Returns:
        float: [description]
    """
    return numpy.roots([-2, 3, 0, -1 * matchproba_bo3])[1]


def get_match_proba_bo5(matchproba_bo3) -> float:
    """Returns the probability for a best of 5 sets match from the probability for a best of 3 sets matches

    Args:
        matchproba_bo3 ([type]): [description]

    Returns:
        float: [description]
    """
    p1 = get_one_set_proba(matchproba_bo3)
    p5 = (p1 ** 3) * (4 - 3 * p1 + (6 * (1 - p1) * (1 - p1)))
    return p5


def fact(x):
    if x in [0, 1]:
        return 1
    r = 1
    for a in range(1, (x + 1)):
        r = r * a
    return r


def ch(a, b):
    return fact(a) / (fact(b) * fact(a - b))


def gameOutcome(s, a, b):
    return ch((a + b), a) * (s ** a) * ((1 - s) ** b) * s


def gameProb(s, v=0, w=0):
    """Calculates the probability of server winning
    ## a single game, given p(winning any given point) [s],
    ## and the current point score.
    ## v, w = current game score, where love = 0, 15 = 1, etc.
    ## - e.g. 30-15 is v=2, w=1
    ## check if game is already over:

    Args:
        s ([type]): [description]
        v (int, optional): [description]. Defaults to 0.
        w (int, optional): [description]. Defaults to 0.

    Returns:
        [type]: [description]
    """
    if v >= 4 and (v - w) >= 2:
        return 1
    elif w >= 4 and (w - v) >= 2:
        return 0
    else:
        pass
    ## if deuce or ad score e.g. 5-4, reduce to e.g. 3-2
    while True:
        if (v + w) > 6:
            v -= 1
            w -= 1
        else:
            break
    ## specific probabilities:
    if w == 0:
        w0 = gameOutcome(s, 3 - v, 0)
    else:
        w0 = 0
    if w <= 1:
        w15 = gameOutcome(s, 3 - v, 1 - w)
    else:
        w15 = 0
    if w <= 2:
        w30 = gameOutcome(s, 3 - v, 2 - w)
    else:
        w30 = 0
    if v == 4:
        wAd, lAd = s, 0
        d = 1 - s
    elif w == 4:
        wAd, lAd = 0, 1 - s
        d = s
    else:
        wAd, lAd = 0, 0
        a = 3 - v
        b = 3 - w
        d = ch((a + b), a) * (s ** a) * ((1 - s) ** b)
    if v <= 2:
        l30 = gameOutcome((1 - s), 3 - w, 2 - v)
    else:
        l30 = 0
    if v <= 1:
        l15 = gameOutcome((1 - s), 3 - w, 1 - v)
    else:
        l15 = 0
    if v == 0:
        l0 = gameOutcome((1 - s), 3 - w, 0)
    else:
        l0 = 0
    ## given d = prob of getting to deuce,
    ## math to divide up further outcomes
    denom = s ** 2 + (1 - s) ** 2
    wd = (d * (s ** 2)) / denom
    ld = (d * ((1 - s) ** 2)) / denom
    win = w0 + w15 + w30 + wd + wAd
    lose = l0 + l15 + l30 + ld + lAd
    return win


##################################################################################
####################################### TB ######################################
##################################################################################


def tiebreakProb(s, t, v=0, w=0, p=7):
    ## calculate the probability that the current server wins a best-of-p tiebreak.
    ## s = p(server wins service point)
    ## t = p(current server wins return point)
    ## v, w = current score
    ## check if tiebreak is already over:
    if v >= p and (v - w) >= 2:
        return 1
    elif w >= p and (w - v) >= 2:
        return 0
    else:
        pass
    ## re-adjust so that point score is not higher than p;
    ## e.g., if p=7 and score is 8-8, adjust to 6-6, which
    ## is logically equivalent
    while True:
        if (v + w) > 2 * (p - 1):
            v -= 1
            w -= 1
        else:
            break
    outcomes = {}  ## track probability of each possible score
    ## this is messy and probably not optimal, figuring out
    ## how many points remain, and how many are on each
    ## player's serve:
    for i in range((p - 1)):
        remain = p + i - v - w
        if remain < 1:
            continue
        else:
            pass
        if remain % 2 == 1:
            if (v + w) % 2 == 0:  ## sr[rs[sr
                if (remain - 1) % 4 == 0:  ## ...s
                    svc = (remain + 1) / 2
                    ret = (remain - 1) / 2
                else:
                    svc = (remain - 1) / 2
                    ret = (remain + 1) / 2
            else:  ## ss[rr[ss[
                if (remain - 1) % 4 == 0:  ## ...s
                    svc = (remain + 1) / 2
                    ret = (remain - 1) / 2
                else:
                    svc = (remain + 1) / 2
                    ret = (remain - 1) / 2
        else:
            if (v + w) % 2 == 0:  ## sr[rs[sr
                svc, ret = remain / 2, remain / 2
            else:  ## ss[rr[ss[
                svc, ret = (remain - 2) / 2, (remain - 2) / 2
                if remain % 4 == 0:
                    svc += 1
                    ret += 1
                else:
                    svc += 2
        ## who serves the last point?
        if (v + w) % 2 == 0:
            ##            if remain in [1, 4, 5, 8, 9, 12, 13, 16, 17, 20, 21]: ## pattern: remain % 4 in [0, 1]
            if (remain % 4) in [0, 1]:
                final = s
                svc -= 1
            else:
                final = t
                ret -= 1
        else:
            ##            if remain in [3, 4, 7, 8, 11, 12, 15, 16, 19, 20]:
            if (remain % 4) in [3, 0]:
                final = t
                ret -= 1
            else:
                final = s
                svc -= 1
        pOutcome = 0
        for j in range(svc + 1):
            for k in range(ret + 1):
                if (j + k) == (p - 1 - v):
                    m = svc - j
                    n = ret - k
                    pr = (
                        (s ** j)
                        * (t ** k)
                        * ((1 - s) ** m)
                        * ((1 - t) ** n)
                        * ch(svc, j)
                        * ch(ret, k)
                        * final
                    )
                    pOutcome += pr
                else:
                    continue
        key = str(p) + str(i)
        outcomes[key] = pOutcome
    if remain % 2 == 1:
        if (v + w) % 2 == 0:  ## sr[rs[sr
            if (remain - 1) % 4 == 0:  ## ...s
                svc = (remain + 1) / 2
                ret = (remain - 1) / 2
            else:
                svc = (remain - 1) / 2
                ret = (remain + 1) / 2
        else:  ## ss[rr[ss[
            if (remain - 1) % 4 == 0:  ## ...s
                svc = (remain + 1) / 2
                ret = (remain - 1) / 2
            else:
                svc = (remain + 1) / 2
                ret = (remain - 1) / 2
    else:
        if (v + w) % 2 == 0:  ## sr[rs[sr
            svc, ret = remain / 2, remain / 2
        else:  ## ss[rr[ss[
            svc, ret = (remain - 2) / 2, (remain - 2) / 2
            if remain % 4 == 0:
                svc += 1
                ret += 1
            else:
                svc += 2
    ## probability of getting to (p-1)-(p-1) (e.g. 6-6)
    final = 1
    x = 0
    for j in range(svc + 1):
        for k in range(ret + 1):
            if (j + k) == (p - 1 - v):
                m = svc - j
                n = ret - k
                pr = (
                    (s ** j)
                    * (t ** k)
                    * ((1 - s) ** m)
                    * ((1 - t) ** n)
                    * ch(svc, j)
                    * ch(ret, k)
                    * final
                )
                x += pr
            else:
                continue
    outcomes["+"] = (x * s * t) / ((s * t) + (1 - s) * (1 - t))
    ## add up all positive outcomes
    wtb = 0
    for z in outcomes:
        wtb += outcomes[z]
    return wtb


##################################################################################
####################################### SET ######################################
##################################################################################


def setOutcome(final, sGames, rGames, vw, g, h):
    pOutcome = 0
    for j in range((sGames + 1)):
        for k in range((rGames + 1)):
            if (j + k) == (6 - 1 - vw):
                m = sGames - j
                n = rGames - k
                p = (
                    (g ** j)
                    * (h ** k)
                    * ((1 - g) ** m)
                    * ((1 - h) ** n)
                    * ch(sGames, j)
                    * ch(rGames, k)
                    * final
                )
                pOutcome += p
            else:
                continue
    return pOutcome


def setGeneral(s, u, v=0, w=0, tb=1):
    ## calculate the probability of the current server winning
    ## a 6-game, tiebreak set, given prob. of server winning any
    ## given service point (s) or return point (u), and the current
    ## game score (v, w)
    ## get prob of current server winning a service game:
    g = gameProb(s)
    ## and current server winning a return game:
    h = gameProb(u)
    ## is set over?
    if tb:
        if v == 7:
            return 1
        elif w == 7:
            return 0
        elif v == 6 and (v - w) > 1:
            return 1
        elif w == 6 and (w - v) > 1:
            return 0
        else:
            pass
    else:
        if v >= 6 and (v - w) > 1:
            return 1
        elif w >= 6 and (w - v) > 1:
            return 0
        else:
            pass
    ## if not over, re-adjust down to no higher than 6-6
    while True:
        if (v + w) > 12:
            v -= 1
            w -= 1
        else:
            break
    ## if no tiebreak, chance that server wins set is ratio of server's prob of winning
    ## two games in a row to returner's prob of winning two games in a row
    if not tb:
        deuceprob = (g * h) / ((g * h) + (1 - g) * (1 - h))
    outcomes = {}
    ## special cases, 11 games or more already
    if (v + w) == 12:
        if tb:
            tp = tiebreakProb(s, u)
            outcomes["76"] = tp
            outcomes["67"] = 1 - tp
        else:
            outcomes["75"] = deuceprob
            outcomes["57"] = 1 - deuceprob
    elif (v + w) == 11:
        if tb:
            tp = tiebreakProb((1 - u), (1 - s))
            if v == 6:
                outcomes["75"] = g
                x = 1 - g
                outcomes["76"] = x * (1 - tp)
                outcomes["67"] = x * tp
            else:
                outcomes["57"] = 1 - g
                x = g
                outcomes["76"] = x * (1 - tp)
                outcomes["67"] = x * tp
        else:
            if v == 6:
                outcomes["75"] = g
                outcomes["57"] = 0
                f = 1 - g  ## f is p(getting to 6-6)
            else:
                outcomes["57"] = 1 - g
                outcomes["75"] = 0
                f = g  ## f is p(getting to 6-6)
            outcomes["75"] += f * deuceprob
            outcomes["57"] += f * (1 - deuceprob)
    else:
        ## win probabilities
        for i in range(5):  ## i = 0
            t = 6 + i - v - w  ## total games remaining in set
            if t < 1:
                continue
            if t % 2 == 0:
                final = h
                sGames = t / 2
                rGames = sGames - 1
            else:
                final = g
                sGames = (t - 1) / 2
                rGames = (t - 1) / 2
            pOutcome = setOutcome(final, sGames, rGames, v, g, h)
            key = "6" + str(i)
            outcomes[key] = pOutcome
        ## loss probabilities
        ## this section isn't necessary, but I wrote it for informal
        ## testing purposes
        for i in range(5):
            t = 6 + i - v - w  ## total games in set; here it's 6
            if t < 1:
                continue
            if t % 2 == 0:
                final = 1 - h
                sGames = t / 2
                rGames = sGames - 1
            else:
                final = 1 - g
                sGames = (t - 1) / 2
                rGames = (t - 1) / 2
            pOutcome = setOutcome(final, sGames, rGames, w, (1 - g), (1 - h))
            key = str(i) + "6"
            outcomes[key] = pOutcome
        ## prob of getting to 5-5
        t = 10 - v - w
        if t % 2 == 0:
            sGames = t / 2
            rGames = t / 2
        else:
            sGames = (t - 1) / 2 + 1
            rGames = (t - 1) / 2
        f = setOutcome(1, sGames, rGames, v, g, h)
        if tb == 1:
            outcomes["75"] = f * g * h
            outcomes["57"] = f * (1 - g) * (1 - h)
            x = f * g * (1 - h) + f * (1 - g) * h  ## p(getting to 6-6)
            if (v + w) % 2 == 0:
                tp = tiebreakProb(s, u)
            else:
                tp = tiebreakProb(u, s)
            outcomes["76"] = x * tp
            outcomes["67"] = x - x * tp
        else:
            outcomes["75"] = f * deuceprob
            outcomes["57"] = f * (1 - deuceprob)
    win = 0
    for o in outcomes:
        if o in ["60", "61", "62", "63", "64", "75", "76"]:
            win += outcomes[o]
        else:
            pass
    return win, outcomes


##################################################################################
##################################### MATCH ######################################
##################################################################################


def matchGeneral(e, v=0, w=0, s=3):
    ## calculates probability of winning the match
    ## from the beginning of a set
    ## e is p(winning a set)
    ## v and w is current set score
    ## s is total number of sets ("best of")
    towin = (s + 1) / 2
    left = towin - v
    if left == 0:
        return 1
    remain = s - v - w
    if left > remain:
        return 0
    win = 0
    for i in range(left, (remain + 1)):
        add = ch((i - 1), (left - 1)) * (e ** (left - 1)) * ((1 - e) ** (i - left)) * e
        win += add
    return win


def matchProb(s, t, gv=0, gw=0, sv=0, sw=0, mv=0, mw=0, sets=3):
    ## calculates probability of winning a match from any given score,
    ## given:
    ## s, t: p(server wins a service point), p(server wins return point)
    ## gv, gw: current score within the game. e.g. 30-15 is 2, 1
    ## sv, sw: current score within the set. e.g. 5, 4
    ## mv, mw: current score within the match (number of sets for each player)
    ## v's are serving player; w's are returning player
    ## sets: "best of", so default is best of 3
    a = gameProb(s)
    b = gameProb(t)
    c = setGeneral(s, t)
    if gv == 0 and gw == 0:  ## no point score
        if sv == 0 and sw == 0:  ## no game score
            return matchGeneral(c, v=mv, w=mw, s=sets)
        else:  ## we're in mid-set, no point score
            sWin = setGeneral(a, b, s, t, v=sv, w=sw)
            sLoss = 1 - sWin
    elif sv == 6 and sw == 6:
        sWin = tiebreakProb(s, t, v=gv, w=gw)
        sLoss = 1 - sWin
    else:
        gWin = gameProb(s, v=gv, w=gw)
        gLoss = 1 - gWin
        sWin = gWin * (
            1 - setGeneral((1 - b), (1 - a), (1 - t), (1 - s), v=sw, w=(sv + 1))
        )
        sWin += gLoss * (
            1 - setGeneral((1 - b), (1 - a), (1 - t), (1 - s), v=(sw + 1), w=sv)
        )
        sLoss = 1 - sWin
    mWin = sWin * matchGeneral(c, v=(mv + 1), w=mw, s=sets)
    mWin += sLoss * matchGeneral(c, v=mv, w=(mw + 1), s=sets)
    return mWin
