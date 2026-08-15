from statistics import mean, pstdev


def calcBeta(xs, ys):
    xs = list(xs)
    ys = list(ys)
    if len(xs) < 2 or len(xs) != len(ys):
        return 1.0

    meanX = mean(xs)
    meanY = mean(ys)
    varX = sum((x - meanX) ** 2 for x in xs) / len(xs)
    if varX == 0:
        return 1.0

    covXY = sum((x - meanX) * (y - meanY) for x, y in zip(xs, ys)) / len(xs)
    return covXY / varX


def rollZScore(values):
    values = list(values)
    if not values:
        return None, None, None

    avg = mean(values)
    std = pstdev(values)
    if std == 0:
        return avg, std, None

    zScore = (values[-1] - avg) / std
    return avg, std, zScore


def calcSpreadWindowStats(spreads):
    spreads = list(spreads)
    if not spreads:
        return None, None, None, None

    avg, std, zScore = rollZScore(spreads)
    return spreads[-1], avg, std, zScore


def calcWindowStats(logA, logB, hedgeRatio):
    logA = list(logA)
    logB = list(logB)
    if not logA or len(logA) != len(logB):
        return None, None, None, None

    spreads = [a - hedgeRatio * b for a, b in zip(logA, logB)]
    return calcSpreadWindowStats(spreads)
