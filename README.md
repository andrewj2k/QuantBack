# QuantBack

QuantBack is a Python backtesting project for building and testing ETF pairs-trading ideas with realistic execution assumptions and train/validation/test evaluation. The data layer supports both CSV and Parquet-backed price stores.

The project now also supports an optional C++ stats extension for the pair-trading math path, so the strategy can keep Python research ergonomics while offloading repeated numerical work to compiled code. That extension now covers both single formulas and full rolling spread-window summaries.

## What It Does

The current project supports:

- multi-symbol daily-bar backtests from a combined price table
- long/short pair trades with multi-leg order handling
- spread trading on log prices
- optional compiled math backend for hedge-ratio and rolling z-score calculations
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

Build the optional C++ extension:

```bash
bash cpp/buildFastStats.sh
```

Validate and benchmark the extension:

```bash
python3 cpp/checkFastStats.py
python3 cpp/benchFastStats.py
```

Run the train/validation/test sweep:

```bash
python3 experiments/tvtSweep.py
```

Benchmark storage format and compiled math:

```bash
python3 experiments/benchStorage.py
python3 cpp/benchFastStats.py
```

## Current Data Universe

The current ETF universe in [data/prices.csv](data/prices.csv) and [data/prices.parquet](data/prices.parquet) includes:

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

## Engineering Results

Measured on this machine with the current 5-symbol 2023 dataset using the reproducible benchmark in `experiments/benchStorage.py`:

- Parquet vs CSV data loads: `11.284 ms` vs `14.212 ms` per load, about `20.6%` faster
- End-to-end backtest runs: `92.491 ms` vs `94.166 ms` per run, about `1.8%` faster
- C++ vs Python `calcBeta`: `0.050640 s` vs `4.035666 s` over `10,000` calls, about `79.7x` faster
- C++ vs Python `rollZScore`: `0.030045 s` vs `2.385154 s`, about `79.4x` faster
- C++ vs Python spread-window stats: `0.052351 s` vs `2.491074 s`, about `47.6x` faster

These improvements matter differently:

- Parquet is a useful systems improvement because it cuts repeated research and data-loading time without changing behavior
- The C++ extension is the larger numerical speedup and is the better resume talking point for quant-dev style engineering

## Resume Framing

Good resume bullet direction for this project:

- built a Python ETF pairs-trading backtester with train/validation/test evaluation, realistic execution costs, risk controls, and multi-symbol portfolio accounting
- added a Parquet-backed market-data path that reduced repeated data-load time by about `21%` versus CSV on the current dataset
- implemented a C++ extension for hedge-ratio and rolling spread-stat calculations, accelerating core numerical kernels by about `48-80x` versus Python

Keep the wording honest:

- say these are benchmarked engineering improvements, not trading alpha
- say the strategy is a mean-reversion ETF pairs strategy using log spreads and rolling z-scores
- do not imply the backtest shows a production-ready edge, because right now it does not

## Recommended Files To Read

- [main.py](main.py)
- [engine/dataFeed.py](engine/dataFeed.py)
- [engine/spreadStats.py](engine/spreadStats.py)
- [engine/fastStats.py](engine/fastStats.py)
- [engine/btEngine.py](engine/btEngine.py)
- [engine/portfolio.py](engine/portfolio.py)
- [engine/exec.py](engine/exec.py)
- [strats/pairStrat.py](strats/pairStrat.py)
- [cpp/fastStats.cpp](cpp/fastStats.cpp)
- [experiments/tvtSweep.py](experiments/tvtSweep.py)
