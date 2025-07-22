import numpy as np
import logging

logger = logging.getLogger(__name__)

class PerformanceEvaluator:
    """
    Calculates strategy performance metrics.
    """

    def evaluate(self, trade_log, equity_curve):
        returns = np.diff(equity_curve) / equity_curve[:-1]

        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        total_return = (equity_curve[-1] / equity_curve[0]) - 1

        logger.info(f"Sharpe: {sharpe:.2f}, Max Drawdown: {max_drawdown:.2%}, Total Return: {total_return:.2%}")

        return {
            "Sharpe Ratio": sharpe,
            "Max Drawdown": max_drawdown,
            "Total Return": total_return
        }

    def _calculate_max_drawdown(self, curve):
        peak = curve[0]
        max_dd = 0
        for val in curve:
            if val > peak:
                peak = val
            drawdown = (peak - val) / peak
            max_dd = max(max_dd, drawdown)
        return max_dd