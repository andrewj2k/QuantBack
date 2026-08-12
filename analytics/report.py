from pathlib import Path

import pandas as pd


def saveRun(results, equityPath, tradesPath):
    """
    Persist core backtest outputs for later analysis and plotting.
    """
    Path(equityPath).parent.mkdir(parents=True, exist_ok=True)
    Path(tradesPath).parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        {
            "Day": list(range(len(results["equityCurve"]))),
            "Equity": results["equityCurve"],
        }
    ).to_csv(equityPath, index=False)

    pd.DataFrame(results["closedTrades"]).to_csv(tradesPath, index=False)


def printStats(metrics):
    print("\nFinal Performance Metrics:")
    for key, value in metrics.items():
        if "Drawdown" in key or "Return" in key:
            print(f"{key}: {value:.2%}")
        else:
            print(f"{key}: {value:.2f}")
