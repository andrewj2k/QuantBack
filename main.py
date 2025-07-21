import yaml
from engine.data_handler import DataHandler
from strategies.dummy_strategy import DummyStrategy
from engine.backtest_engine import BacktestEngine

# 1. Load config
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

source = config["source"]
start_date = config["start_date"]
end_date = config["end_date"]

# 2. Initialize
data_handler = DataHandler(source=source, start_date=start_date, end_date=end_date)
strategy = DummyStrategy()

# For now, pass None for execution, portfolio, evaluator
engine = BacktestEngine(
    data_handler=data_handler,
    strategy=strategy,
    execution_handler=None,
    portfolio=None,
    evaluator=None
)

# 3. Run backtest
engine.run()