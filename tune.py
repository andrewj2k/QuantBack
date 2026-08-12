from engine.dataFeed import DataFeed
from strats.dummyStrat import DummyStrat
from engine.exec import Exec
from engine.portfolio import Portfolio
from engine.perf import PerfEval
import numpy as np
import pandas as pd
import os

os.makedirs("logs/tuning", exist_ok=True)

results = []

for n in range(1, 11):  # try buyEveryN from 1 to 10
    dataFeed = DataFeed("data/SPY.csv", "2023-01-03", "2023-12-31")
    strat = DummyStrat(buyEveryN=n)
    exec = Exec()
    portfolio = Portfolio(100000)
    perfEval = PerfEval()

    equityCurve = []
    trades = []

    while dataFeed.idx < len(dataFeed.df):
        bar = dataFeed.nextBar()
        signal = strat.genSig(bar)

        if signal:
            trade = exec.fill(signal, bar["close"], bar["date"])
            if trade:
                portfolio.onSignal(trade["side"], bar)
                trades.append(trade)

        equityCurve.append(portfolio.mktVal)

    metrics = perfEval.calc(trades, np.array(equityCurve))
    results.append({
        "buyEveryN": n,
        **metrics,
    })

# Save raw results
df = pd.DataFrame(results)
df.to_csv("logs/tuning/dummyStratTuning.csv", index=False)

# --- 1. Visualization ---
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(df["buyEveryN"], df["Sharpe Ratio"], marker='o', label="Sharpe Ratio")
plt.plot(df["buyEveryN"], df["Max Drawdown"], marker='o', label="Max Drawdown")
plt.plot(df["buyEveryN"], df["Total Return"], marker='o', label="Total Return")
plt.xlabel("Buy Every N Bars")
plt.ylabel("Metric Value")
plt.title("Parameter Sweep: Dummy Strategy")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("logs/tuning/paramSweep.png")
plt.show()

# --- 2. Scoring function ---
# Weights: +0.5 * Sharpe, -5 * Drawdown, +0.5 * Total Return
df["Score"] = (
    0.5 * df["Sharpe Ratio"]
    - 5.0 * df["Max Drawdown"]
    + 0.5 * df["Total Return"]
)

# Sort by Score
df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
df.to_csv("logs/tuning/dummyStratRanked.csv", index=False)

# Print top result
print("\nTop Configuration by Weighted Score:")
print(df.iloc[0])
