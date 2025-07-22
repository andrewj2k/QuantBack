import logging
from config.config_loader import load_config
from engine.data_handler import DataHandler
from engine.execution_handler import ExecutionHandler
from engine.portfolio import Portfolio
from engine.performance import PerformanceEvaluator
from strategies.dummy_strategy import DummyStrategy

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load config
config = load_config("config.yaml")
source = config["data"]["source"]
start_date = config["data"]["start_date"]
end_date = config["data"]["end_date"]
initial_cash = config["portfolio"]["initial_cash"]

# Instantiate components
data_handler = DataHandler(source=source, start_date=start_date, end_date=end_date)
strategy = DummyStrategy()  # replace with config-based strategy selection later
execution_handler = ExecutionHandler()
portfolio = Portfolio(initial_cash)
evaluator = PerformanceEvaluator()

equity_curve = []
last_close = 0

# Run backtest loop
bar = data_handler.get_next_bar()
while bar is not None:
    last_close = bar["Close"]

    signal = strategy.generate_signal(bar)

    if signal:
        trade = execution_handler.execute_trade(signal, bar["Close"], bar["Date"])
        if trade:
            portfolio.execute_signal(signal, bar)

    equity_curve.append(portfolio.market_value)
    bar = data_handler.get_next_bar()

# Final PnL
print(f"\nFinal PnL: ${portfolio.market_value:,.2f}")

# Evaluate performance
results = evaluator.evaluate([], equity_curve)
print("\nPerformance Metrics:")
for k, v in results.items():
    print(f"{k}: {v:.2%}" if isinstance(v, float) else f"{k}: {v}")