from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.fastStats import calcBeta, calcWindowStats, rollZScore
from engine.spreadStats import calcBeta as pyCalcBeta
from engine.spreadStats import calcWindowStats as pyCalcWindowStats
from engine.spreadStats import rollZScore as pyRollZScore


def main():
    xs = [5.10, 5.12, 5.08, 5.11, 5.15]
    ys = [5.05, 5.09, 5.04, 5.06, 5.10]
    spreads = [0.01, -0.02, 0.00, 0.03, -0.01]

    pyBeta = pyCalcBeta(xs, ys)
    cppBeta = calcBeta(xs, ys, backend="cpp")
    pyAvg, pyStd, pyZ = pyRollZScore(spreads)
    cppAvg, cppStd, cppZ = rollZScore(spreads, backend="cpp")
    pySpreadStats = pyCalcWindowStats(xs, ys, 0.9)
    cppSpreadStats = calcWindowStats(xs, ys, 0.9, backend="cpp")

    print("beta:", pyBeta, cppBeta)
    print("zscore:", (pyAvg, pyStd, pyZ), (cppAvg, cppStd, cppZ))
    print("window:", pySpreadStats, cppSpreadStats)


if __name__ == "__main__":
    main()
