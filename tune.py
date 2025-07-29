from engine.data_handler import DataHandler
from strategies.dummy_strategy import DummyStrategy
from engine.execution_handler import ExecutionHandler
from engine.portfolio import Portfolio
from engine.performance import PerformanceEvaluator
import numpy as np
import pandas as pd
import os

os.makedirs("logs/tuning", exist_ok=True)

results = []

for n in range(1, 11):  # try buy_every_n from 1 to 10
    data_handler = DataHandler("data/SPY.csv", "2023-01-03", "2023-12-31")
    strategy = DummyStrategy(buy_every_n=n)
    execution_handler = ExecutionHandler()
    portfolio = Portfolio(100000)
    evaluator = PerformanceEvaluator()

    equity_curve = []
    trade_log = []

    while data_handler.current_index < len(data_handler.df):
        bar = data_handler.get_next_bar()
        signal = strategy.generate_signal(bar)

        if signal:
            trade = execution_handler.execute_trade(signal, bar["close"], bar["date"])
            if trade:
                portfolio.execute_signal(trade["side"], bar)
                trade_log.append(trade)

        equity_curve.append(portfolio.market_value)

    metrics = evaluator.evaluate(trade_log, np.array(equity_curve))
    results.append({
        "buy_every_n": n,
        **metrics
    })

# Save raw results
df = pd.DataFrame(results)
df.to_csv("logs/tuning/dummy_strategy_tuning.csv", index=False)

# --- 1. Visualization ---
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(df["buy_every_n"], df["Sharpe Ratio"], marker='o', label="Sharpe Ratio")
plt.plot(df["buy_every_n"], df["Max Drawdown"], marker='o', label="Max Drawdown")
plt.plot(df["buy_every_n"], df["Total Return"], marker='o', label="Total Return")
plt.xlabel("Buy Every N Bars")
plt.ylabel("Metric Value")
plt.title("Parameter Sweep: Dummy Strategy")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("logs/tuning/parameter_sweep_plot.png")
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
df.to_csv("logs/tuning/dummy_strategy_ranked.csv", index=False)

# Print top result
print("\nTop Configuration by Weighted Score:")
print(df.iloc[0])