# Experiment Summary

## Goal

The current experiment workflow tests whether ETF pairs-trading behavior is more convincing when:

- the pair itself is selected from a small candidate universe
- the spread uses either a unit hedge or a static beta hedge
- the strategy is evaluated on separate train, validation, and test windows

## Candidate Pairs

- `SPY / IVV`
- `SPY / VOO`
- `IVV / VOO`
- `QQQ / XLK`

## Hedge Modes

- `unit`
- `staticBeta`

`unit` assumes a 1:1 relationship.

`staticBeta` estimates:

- `beta = cov(logB, logA) / var(logB)`

from the warmup window, then trades:

- `spread = logA - beta * logB`

## Evaluation Setup

The experiment script [experiments/tvtSweep.py](/Users/andrewjiang/QuantBack/experiments/tvtSweep.py) uses:

- train: `2023-01-03` to `2023-06-30`
- validation: `2023-07-03` to `2023-09-29`
- test: `2023-10-02` to `2023-12-29`

It sweeps over:

- `lookback`: `20`, `30`
- `entryZ`: `1.5`, `2.0`
- `exitZ`: `0.2`, `0.3`

## Best Validation Choice

From [logs/experiments/bestValChoice.txt](/Users/andrewjiang/QuantBack/logs/experiments/bestValChoice.txt):

- pair: `IVV / VOO`
- hedge mode: `staticBeta`
- lookback: `30`
- entryZ: `2.0`
- exitZ: `0.2`

Validation stats:

- Sharpe: `1.5325`
- Return: `0.1353%`
- Drawdown: `0.0468%`

## Interpretation

The key research takeaway is not just that one row looked best.

The more important lesson is:

- pair choice matters
- hedge ratio choice matters
- validation winners do not automatically remain strong on test

This means the project is already useful as a research framework, even though the current strategy is not yet robust enough to claim a durable trading edge.

## Useful Output Files

- [logs/experiments/tvtLong.csv](/Users/andrewjiang/QuantBack/logs/experiments/tvtLong.csv)
- [logs/experiments/tvtSummary.csv](/Users/andrewjiang/QuantBack/logs/experiments/tvtSummary.csv)
- [logs/experiments/bestValChoice.txt](/Users/andrewjiang/QuantBack/logs/experiments/bestValChoice.txt)
