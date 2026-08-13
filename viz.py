import matplotlib.pyplot as plt
import pandas as pd

# --- 1. Load and plot equity curve ---
equityDf = pd.read_csv("logs/equityCurve.csv")

plt.figure(figsize=(12, 6))
plt.plot(equityDf["Day"], equityDf["Equity"], label="Equity Curve")
plt.xlabel("Day")
plt.ylabel("Portfolio Value ($)")
plt.title("Strategy Equity Curve")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("logs/equityCurvePlot.png")
plt.show()

# --- 2. Drawdown visualization ---
equity = equityDf["Equity"]
rollingMax = equity.cummax()
drawdown = (rollingMax - equity) / rollingMax

plt.figure(figsize=(12, 3))
plt.fill_between(equityDf["Day"], drawdown, color="red", alpha=0.3)
plt.title("Drawdown Over Time")
plt.ylabel("Drawdown (%)")
plt.tight_layout()
plt.savefig("logs/drawdownPlot.png")
plt.show()

# --- 3. Trade outcome statistics ---
trades = pd.read_csv("logs/tradeLog.csv")
trades["returnPct"] = (trades["exit_price"] - trades["entry_price"]) / trades["entry_price"] * 100

winRate = (trades["pnl"] > 0).mean()
avgWin = trades[trades["pnl"] > 0]["pnl"].mean()
avgLoss = trades[trades["pnl"] < 0]["pnl"].mean()
expectancy = (winRate * avgWin) + ((1 - winRate) * avgLoss)

print("\n--- Trade Performance Summary ---")
print(f"Total Trades: {len(trades)}")
print(f"Win Rate: {winRate:.2%}")
print(f"Avg Win: ${avgWin:.2f}")
print(f"Avg Loss: ${avgLoss:.2f}")
print(f"Expectancy per Trade: ${expectancy:.2f}")

# --- 4. Pair signal diagnostics ---
signalDf = pd.read_csv("logs/pairSignal.csv")
signalDf["date"] = pd.to_datetime(signalDf["date"])
signalDf = signalDf.dropna(subset=["spread", "zScore"])

plt.figure(figsize=(12, 6))
plt.plot(signalDf["date"], signalDf["spread"], label="Spread")
plt.plot(signalDf["date"], signalDf["spreadMean"], label="Rolling Mean")
plt.title("Pair Spread Over Time")
plt.xlabel("Date")
plt.ylabel("Spread")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("logs/pairSpreadPlot.png")
plt.show()

plt.figure(figsize=(12, 4))
plt.plot(signalDf["date"], signalDf["zScore"], label="Z-Score")
plt.axhline(0, color="black", linewidth=1)
plt.axhline(1.5, color="red", linestyle="--", linewidth=1)
plt.axhline(-1.5, color="red", linestyle="--", linewidth=1)
plt.axhline(0.3, color="green", linestyle="--", linewidth=1)
plt.axhline(-0.3, color="green", linestyle="--", linewidth=1)
plt.title("Pair Z-Score Over Time")
plt.xlabel("Date")
plt.ylabel("Z-Score")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("logs/pairZScorePlot.png")
plt.show()
