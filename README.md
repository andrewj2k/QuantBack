# QuantBack

QuantBack is a Python backtesting project for building and testing ETF pairs-trading ideas with realistic execution assumptions and train/validation/test evaluation.

## What It Does

The current project supports:

- multi-symbol daily-bar backtests from a combined price table
- long/short pair trades with multi-leg order handling
- spread trading on log prices
- two hedge modes:
  - `unit`: assumes a 1:1 relationship
  - `staticBeta`: estimates a fixed hedge ratio from the warmup window
- execution realism:
  - slippage in basis points
  - per-order commissions
- basic risk controls:
  - max package capital fraction
  - max dollars per leg
  - stop-loss
  - max holding period
- signal diagnostics:
  - spread
  - rolling mean/std
  - z-score
  - hedge ratio
  - package PnL / return
- experiment sweeps across:
  - train / validation / test windows
  - candidate ETF pairs
  - hedge modes
  - strategy parameters

## Current Strategy

The main strategy in [strats/pairStrat.py](strats/pairStrat.py) works like this:

1. Pick two ETFs, such as `IVV` and `VOO`.
2. Transform prices into log prices.
3. Build a spread:
   - `unit`: `log(A) - log(B)`
   - `staticBeta`: `log(A) - beta * log(B)`
4. Compute a rolling z-score of that spread.
5. Enter when the spread is far from its rolling mean:
   - low z-score: buy `A`, sell `B`
   - high z-score: sell `A`, buy `B`
6. Exit when:
   - the spread mean reverts,
   - the trade loses too much,
   - or the trade stays open too long.

## Project Structure

- `main.py`: runs one configured backtest
- `engine/`: data feed, execution, portfolio accounting, performance evaluation, backtest loop
- `strats/`: strategy interfaces and strategy implementations
- `analytics/`: helpers for saving run outputs
- `config/`: runtime configuration
- `data/`: combined ETF price data
- `experiments/`: multi-run research scripts
- `logs/`: generated backtest and experiment outputs

## How To Run

Run one configured backtest:

```bash
python3 main.py
```

Run the train/validation/test sweep:

```bash
python3 experiments/tvtSweep.py
```

## Current Data Universe

The current ETF universe in [data/prices.csv](data/prices.csv) includes:

- `SPY`
- `IVV`
- `VOO`
- `QQQ`
- `XLK`

## Latest Experiment Snapshot

The latest validation winner from [logs/experiments/bestValChoice.txt](logs/experiments/bestValChoice.txt) was:

- pair: `IVV / VOO`
- hedge mode: `staticBeta`
- lookback: `30`
- entry z-score: `2.0`
- exit z-score: `0.2`

Important caveat:

- this looked best on validation, but the broader train/validation/test results still show that the strategy is fragile after costs
- the project is currently stronger as a research/infrastructure artifact than as proof of a durable edge

## Recommended Files To Read

- [main.py](main.py)
- [engine/dataFeed.py](engine/dataFeed.py)
- [engine/btEngine.py](engine/btEngine.py)
- [engine/portfolio.py](engine/portfolio.py)
- [engine/exec.py](engine/exec.py)
- [strats/pairStrat.py](strats/pairStrat.py)
- [experiments/tvtSweep.py](experiments/tvtSweep.py)

