from engine.data_handler import DataHandler
from strategies.dummy_strategy import DummyStrategy
from engine.execution_handler import ExecutionHandler
from engine.portfolio import Portfolio
from engine.performance import PerformanceEvaluator
import numpy as np

# --- Config ---
source = "data/SPY.csv"
start_date = "2023-01-03"
end_date = "2023-12-31"
initial_cash = 100000

# --- Initialize components ---
data_handler = DataHandler(source=source, start_date=start_date, end_date=end_date)
strategy = DummyStrategy()  # Plug in your actual strategy here
execution_handler = ExecutionHandler()
portfolio = Portfolio(initial_cash)
evaluator = PerformanceEvaluator()

# --- Tracking ---
equity_curve = []
trade_log = []

# --- Main backtest loop ---
while data_handler.current_index < len(data_handler.df):
    bar = data_handler.get_next_bar()
    signal = strategy.generate_signal(bar)  # 'BUY', 'SELL', or None

    if signal:
        trade = execution_handler.execute_trade(signal, price=bar["close"], timestamp=bar["date"])
        if trade:
            portfolio.execute_signal(trade["side"], bar)
            trade_log.append(trade)

    equity_curve.append(portfolio.market_value)
    print(f"Day {data_handler.current_index}: Portfolio = ${portfolio.market_value:.2f}")

# --- Evaluate and report performance ---
results = evaluator.evaluate(trade_log, np.array(equity_curve))
import pandas as pd

# --- Export equity curve ---
pd.DataFrame({
    "Day": list(range(len(equity_curve))),
    "Equity": equity_curve
}).to_csv("logs/equity_curve.csv", index=False)

# --- Export closed trades ---
pd.DataFrame(portfolio.closed_trades).to_csv("logs/trade_log.csv", index=False)

print("\nFinal Performance Metrics:")
for key, value in results.items():
    if "Drawdown" in key or "Return" in key:
        print(f"{key}: {value:.2%}")
    else:
        print(f"{key}: {value:.2f}")