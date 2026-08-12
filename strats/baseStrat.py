from abc import ABC, abstractmethod


class BaseStrat(ABC):
    """
    Base interface for any strategy that emits one order or a list of orders.
    """

    @abstractmethod
    def genSig(self, snap, portfolio):
        """
        snap: dict with keys:
          - date
          - bars: {symbol: {open, high, low, close, volume}}
        portfolio: current portfolio state, useful for exit rules

        Returns:
          - None
          - {"symbol": "SPY", "side": "BUY"}
          - {"symbol": "SPY", "side": "SELL"}
          - [
                {"symbol": "SPY", "side": "BUY"},
                {"symbol": "IVV", "side": "SELL"},
            ]
        """
        pass
