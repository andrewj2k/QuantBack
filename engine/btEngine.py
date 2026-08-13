import numpy as np


class BtEngine:
    """
    Orchestrates the backtest simulation loop and returns raw results.
    """

    def __init__(self, dataFeed, strat, exec, portfolio, perfEval):
        self.dataFeed = dataFeed
        self.strat = strat
        self.exec = exec
        self.portfolio = portfolio
        self.perfEval = perfEval

    def run(self):
        """
        Main loop:
        1. Get snapshot
        2. Generate order(s)
        3. Execute trade(s)
        4. Update portfolio
        5. Evaluate results
        """
        equityCurve = []
        trades = []

        while self.dataFeed.idx < len(self.dataFeed.dates):
            snap = self.dataFeed.nextSnap()
            self.portfolio.markToMkt(snap)
            orders = self.strat.genSig(snap, self.portfolio)

            if orders:
                if isinstance(orders, dict):
                    orders = [orders]
                fills = self.exec.fillOrders(orders, snap)
                if fills:
                    self.portfolio.onTrades(fills, snap)
                    trades.extend(fills)

            equityCurve.append(self.portfolio.mktVal)

        metrics = self.perfEval.calc(trades, np.array(equityCurve, dtype=float))

        return {
            "equityCurve": equityCurve,
            "trades": trades,
            "closedTrades": self.portfolio.closedTrades,
            "signalLog": getattr(self.strat, "signalLog", []),
            "metrics": metrics,
        }
