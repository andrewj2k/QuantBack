from engine.spreadStats import calcBeta as pyCalcBeta
from engine.spreadStats import calcSpreadWindowStats as pyCalcSpreadWindowStats
from engine.spreadStats import calcWindowStats as pyCalcWindowStats
from engine.spreadStats import rollZScore as pyRollZScore

try:
    from engine import fastStatsCpp as cppStats
except ImportError:
    cppStats = None


def hasCpp():
    return cppStats is not None


def pickBackend(preferred="auto"):
    if preferred not in {"auto", "python", "cpp"}:
        raise ValueError(f"Unsupported math backend: {preferred}")

    if preferred == "auto":
        return "cpp" if hasCpp() else "python"
    if preferred == "cpp" and not hasCpp():
        raise RuntimeError("C++ math backend requested but extension is not built")
    return preferred


def calcBeta(xs, ys, backend="auto"):
    backend = pickBackend(backend)
    if backend == "cpp":
        return cppStats.calc_beta(list(xs), list(ys))
    return pyCalcBeta(xs, ys)


def rollZScore(values, backend="auto"):
    backend = pickBackend(backend)
    if backend == "cpp":
        avg, std, zScore = cppStats.roll_zscore(list(values))
        if std == 0.0:
            return avg, std, None
        return avg, std, zScore
    return pyRollZScore(values)


def calcWindowStats(logA, logB, hedgeRatio, backend="auto"):
    backend = pickBackend(backend)
    if backend == "cpp":
        latestSpread, avg, std, zScore = cppStats.calc_window_stats(
            list(logA),
            list(logB),
            hedgeRatio,
        )
        if std == 0.0:
            return latestSpread, avg, std, None
        return latestSpread, avg, std, zScore
    return pyCalcWindowStats(logA, logB, hedgeRatio)


def calcSpreadWindowStats(spreads, backend="auto"):
    backend = pickBackend(backend)
    if backend == "cpp":
        latestSpread, avg, std, zScore = cppStats.calc_spread_window_stats(list(spreads))
        if std == 0.0:
            return latestSpread, avg, std, None
        return latestSpread, avg, std, zScore
    return pyCalcSpreadWindowStats(spreads)
