from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.fastStats import calcBeta, calcWindowStats, rollZScore, hasCpp


def buildSeries(n=252):
    xs = []
    ys = []
    spreads = []
    x = 5.0
    y = 5.0
    for _ in range(n):
        x += random.uniform(-0.02, 0.02)
        y += random.uniform(-0.02, 0.02)
        xs.append(x)
        ys.append(y)
        spreads.append(x - y)
    return xs, ys, spreads


def timeCalls(label, loops, fn):
    start = time.perf_counter()
    for _ in range(loops):
        fn()
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.6f}s")
    return elapsed


def main():
    xs, ys, spreads = buildSeries()
    loops = 10000

    pyBeta = timeCalls("python calcBeta", loops, lambda: calcBeta(xs, ys, backend="python"))
    pyZ = timeCalls("python rollZScore", loops, lambda: rollZScore(spreads, backend="python"))
    pyWindow = timeCalls(
        "python calcWindowStats",
        loops,
        lambda: calcWindowStats(xs, ys, 0.9, backend="python"),
    )

    if not hasCpp():
        print("cpp backend not built; run: bash cpp/buildFastStats.sh")
        return

    cppBeta = timeCalls("cpp calcBeta", loops, lambda: calcBeta(xs, ys, backend="cpp"))
    cppZ = timeCalls("cpp rollZScore", loops, lambda: rollZScore(spreads, backend="cpp"))
    cppWindow = timeCalls(
        "cpp calcWindowStats",
        loops,
        lambda: calcWindowStats(xs, ys, 0.9, backend="cpp"),
    )

    print(f"beta speedup: {pyBeta / cppBeta:.2f}x")
    print(f"zscore speedup: {pyZ / cppZ:.2f}x")
    print(f"window speedup: {pyWindow / cppWindow:.2f}x")


if __name__ == "__main__":
    main()
