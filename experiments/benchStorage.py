from copy import deepcopy
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.configLoader import loadConfig
from engine.dataFeed import DataFeed
from main import runBacktest


LOAD_LOOPS = 200
RUN_LOOPS = 40


def benchLoads(source, symbols, startDate, endDate, loops=LOAD_LOOPS):
    t0 = perf_counter()
    rows = None
    dates = None

    for _ in range(loops):
        feed = DataFeed(source, symbols, startDate, endDate)
        rows = len(feed.df)
        dates = len(feed.dates)

    elapsed = perf_counter() - t0
    return {
        "source": source,
        "loops": loops,
        "rows": rows,
        "dates": dates,
        "seconds": elapsed,
        "perLoadMs": elapsed / loops * 1000,
    }


def benchRuns(source, baseCfg, loops=RUN_LOOPS):
    cfg = deepcopy(baseCfg)
    cfg["data"]["source"] = source

    t0 = perf_counter()
    metrics = None
    for _ in range(loops):
        results = runBacktest(cfg, saveOutputs=False, printSummary=False)
        metrics = results["metrics"]

    elapsed = perf_counter() - t0
    return {
        "source": source,
        "loops": loops,
        "seconds": elapsed,
        "perRunMs": elapsed / loops * 1000,
        "metrics": metrics,
    }


def fmtPctDiff(base, other):
    return (base - other) / base * 100


def main():
    cfg = loadConfig()
    symbols = cfg["data"]["symbols"]
    startDate = cfg["backtest"]["startDate"]
    endDate = cfg["backtest"]["endDate"]

    csvLoad = benchLoads("data/prices.csv", symbols, startDate, endDate)
    pqLoad = benchLoads("data/prices.parquet", symbols, startDate, endDate)
    csvRun = benchRuns("data/prices.csv", cfg)
    pqRun = benchRuns("data/prices.parquet", cfg)

    print("Load benchmark")
    print(csvLoad)
    print(pqLoad)
    print(f"Parquet load speedup: {fmtPctDiff(csvLoad['seconds'], pqLoad['seconds']):.2f}%")
    print()

    print("Backtest benchmark")
    print(csvRun)
    print(pqRun)
    print(f"Parquet backtest speedup: {fmtPctDiff(csvRun['seconds'], pqRun['seconds']):.2f}%")


if __name__ == "__main__":
    main()
