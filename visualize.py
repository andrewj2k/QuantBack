import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Load and plot equity curve ---
equity_df = pd.read_csv("logs/equity_curve.csv")

plt.figure(figsize=(12, 6))
plt.plot(equity_df["Day"], equity_df["Equity"], label="Equity Curve")
plt.xlabel("Day")
plt.ylabel("Portfolio Value ($)")
plt.title("Strategy Equity Curve")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("logs/equity_curve_plot.png")
plt.show()

# --- 2. Drawdown visualization ---
equity = equity_df["Equity"]
rolling_max = equity.cummax()
drawdown = (rolling_max - equity) / rolling_max

plt.figure(figsize=(12, 3))
plt.fill_between(equity_df["Day"], drawdown, color="red", alpha=0.3)
plt.title("Drawdown Over Time")
plt.ylabel("Drawdown (%)")
plt.tight_layout()
plt.savefig("logs/drawdown_plot.png")
plt.show()

# --- 3. Trade outcome statistics ---
trades = pd.read_csv("logs/trade_log.csv")
trades["return_pct"] = (trades["exit_price"] - trades["entry_price"]) / trades["entry_price"] * 100

win_rate = (trades["pnl"] > 0).mean()
avg_win = trades[trades["pnl"] > 0]["pnl"].mean()
avg_loss = trades[trades["pnl"] < 0]["pnl"].mean()
expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

print("\n--- Trade Performance Summary ---")
print(f"Total Trades: {len(trades)}")
print(f"Win Rate: {win_rate:.2%}")
print(f"Avg Win: ${avg_win:.2f}")
print(f"Avg Loss: ${avg_loss:.2f}")
print(f"Expectancy per Trade: ${expectancy:.2f}")