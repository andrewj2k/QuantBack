# QuantBack

QuantBack is a modular backtesting project for learning how to design trading research infrastructure.

## Current Status

The project currently supports a basic single-asset backtest with modular components for data handling, strategy logic, execution, portfolio accounting, and performance evaluation.

## Project Structure

- `main.py`: wires the run together by loading config, building modules, and kicking off the backtest
- `engine/`: the core mechanics: data loading, fills, portfolio state, performance stats, and the backtest loop
- `strats/`: strategy classes that turn market data into BUY/SELL/None decisions
- `analytics/`: save outputs and print run summaries
- `config/`: runtime settings like dates, data source, and strategy params
- `data/`: raw input CSVs
- `logs/`: generated run outputs and plots

## How to Run

```bash
python3 main.py
```

## Roadmap

- Multi-symbol support
- Pairs trading strategy
- Transaction costs and slippage
- Walk-forward validation
- Improved analytics and visualization
