import numpy as np
import logging

logger = logging.getLogger(__name__)


class PerfEval:
    """
    Calculates strategy performance metrics.
    """

    def calc(self, trades, equity):
        if len(equity) < 2:
            return {
                "Sharpe Ratio": 0.0,
                "Max Drawdown": 0.0,
                "Total Return": 0.0,
            }

        returns = np.diff(equity) / equity[:-1]
        returns = returns[np.isfinite(returns)]

        sharpe = (
            np.mean(returns) / np.std(returns) * np.sqrt(252)
            if len(returns) > 0 and np.std(returns) > 0 else 0
        )
        maxDrawdown = self._calcMaxDd(equity)
        totalReturn = (equity[-1] / equity[0]) - 1

        logger.info(
            f"Sharpe: {sharpe:.2f}, Max Drawdown: {maxDrawdown:.2%}, Total Return: {totalReturn:.2%}"
        )

        return {
            "Sharpe Ratio": sharpe,
            "Max Drawdown": maxDrawdown,
            "Total Return": totalReturn,
        }

    def _calcMaxDd(self, curve):
        if len(curve) == 0:
            return 0.0

        peak = curve[0]
        maxDd = 0
        for val in curve:
            peak = max(peak, val)
            drawdown = (peak - val) / peak
            maxDd = max(maxDd, drawdown)
        return maxDd
