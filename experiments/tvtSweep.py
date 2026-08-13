from itertools import product
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.configLoader import loadConfig
from main import runBacktest, withOverrides


SPLITS = {
    "train": ("2023-01-03", "2023-06-30"),
    "val": ("2023-07-03", "2023-09-29"),
    "test": ("2023-10-02", "2023-12-29"),
}

PARAM_GRID = {
    "lookback": [20, 30],
    "entryZ": [1.5, 2.0],
    "exitZ": [0.2, 0.3],
}

PAIR_UNIVERSE = [
    ("SPY", "IVV"),
    ("SPY", "VOO"),
    ("IVV", "VOO"),
    ("QQQ", "XLK"),
]

HEDGE_MODES = ["unit", "staticBeta"]

OUT_DIR = Path("logs/experiments")


def iterGrid(grid):
    keys = list(grid.keys())
    for values in product(*(grid[key] for key in keys)):
        yield dict(zip(keys, values))


def runSplit(cfg, splitName, startDate, endDate, stratParams, symbols):
    splitCfg = withOverrides(
        cfg,
        startDate=startDate,
        endDate=endDate,
        stratParams=stratParams,
        symbols=symbols,
    )
    results = runBacktest(splitCfg, saveOutputs=False, printSummary=False)
    metrics = results["metrics"]
    return {
        "split": splitName,
        "startDate": startDate,
        "endDate": endDate,
        **stratParams,
        "sharpe": metrics["Sharpe Ratio"],
        "maxDrawdown": metrics["Max Drawdown"],
        "totalReturn": metrics["Total Return"],
        "numClosedLegs": len(results["closedTrades"]),
        "numSignalRows": len(results.get("signalLog", [])),
    }


def scoreVal(row):
    """
    Validation score used only to rank parameter sets.

    This is intentionally simple and transparent:
    - higher Sharpe is better
    - higher total return is better
    - larger drawdown is worse
    """
    return row["sharpe"] + 0.5 * row["totalReturn"] - row["maxDrawdown"]


def main():
    cfg = loadConfig()
    rows = []

    for symA, symB in PAIR_UNIVERSE:
        for hedgeMode in HEDGE_MODES:
            for stratParams in iterGrid(PARAM_GRID):
                fullParams = {
                    "symA": symA,
                    "symB": symB,
                    "hedgeMode": hedgeMode,
                    **stratParams,
                }
                print(f"Running params: {fullParams}")
                for splitName, (startDate, endDate) in SPLITS.items():
                    rows.append(
                        runSplit(
                            cfg,
                            splitName,
                            startDate,
                            endDate,
                            fullParams,
                            symbols=sorted({symA, symB}),
                        )
                    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    longDf = pd.DataFrame(rows)
    longPath = OUT_DIR / "tvtLong.csv"
    longDf.to_csv(longPath, index=False)

    wideDf = (
        longDf
        .pivot_table(
            index=["symA", "symB", "hedgeMode", "lookback", "entryZ", "exitZ"],
            columns="split",
            values=["sharpe", "maxDrawdown", "totalReturn", "numClosedLegs"],
        )
        .sort_index(axis=1)
    )
    wideDf.columns = [f"{metric}_{split}" for metric, split in wideDf.columns]
    wideDf = wideDf.reset_index()

    valRows = longDf[longDf["split"] == "val"].copy()
    valRows["valScore"] = valRows.apply(scoreVal, axis=1)
    bestVal = (
        valRows
        .sort_values(["valScore", "sharpe", "totalReturn"], ascending=False)
        .iloc[0]
    )

    wideDf["isBestVal"] = (
        (wideDf["lookback"] == bestVal["lookback"]) &
        (wideDf["symA"] == bestVal["symA"]) &
        (wideDf["symB"] == bestVal["symB"]) &
        (wideDf["hedgeMode"] == bestVal["hedgeMode"]) &
        (wideDf["entryZ"] == bestVal["entryZ"]) &
        (wideDf["exitZ"] == bestVal["exitZ"])
    )
    wideDf["valScore"] = wideDf.apply(
        lambda row: scoreVal({
            "sharpe": row["sharpe_val"],
            "totalReturn": row["totalReturn_val"],
            "maxDrawdown": row["maxDrawdown_val"],
        }),
        axis=1,
    )
    wideDf = wideDf.sort_values(["isBestVal", "valScore"], ascending=[False, False])

    widePath = OUT_DIR / "tvtSummary.csv"
    wideDf.to_csv(widePath, index=False)

    bestPath = OUT_DIR / "bestValChoice.txt"
    bestPath.write_text(
        "\n".join([
            "Best parameter set by validation score:",
            f"symA={bestVal['symA']}",
            f"symB={bestVal['symB']}",
            f"hedgeMode={bestVal['hedgeMode']}",
            f"lookback={int(bestVal['lookback'])}",
            f"entryZ={bestVal['entryZ']}",
            f"exitZ={bestVal['exitZ']}",
            f"valSharpe={bestVal['sharpe']:.4f}",
            f"valReturn={bestVal['totalReturn']:.4%}",
            f"valDrawdown={bestVal['maxDrawdown']:.4%}",
            f"valScore={bestVal['valScore']:.6f}",
        ])
    )

    print(f"Saved long results to {longPath}")
    print(f"Saved summary results to {widePath}")
    print(bestPath.read_text())


if __name__ == "__main__":
    main()
