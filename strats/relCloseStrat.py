from strats.baseStrat import BaseStrat


class RelCloseStrat(BaseStrat):
    """
    Simple Day 2 sanity strategy.

    It compares the closes of two symbols on the same date and proves that the
    strategy can read a multi-symbol snapshot and emit a symbol-specific order.
    """

    def __init__(self, anchorSym="SPY", compareSym="IVV"):
        self.anchorSym = anchorSym
        self.compareSym = compareSym

    def genSig(self, snap, portfolio):
        bars = snap["bars"]
        if self.anchorSym not in bars or self.compareSym not in bars:
            return None

        anchorClose = bars[self.anchorSym]["close"]
        compareClose = bars[self.compareSym]["close"]

        # goal is validation, not alpha yet
        if portfolio.isFlat and anchorClose < compareClose:
            return {"symbol": self.anchorSym, "side": "BUY"}

        if portfolio.hasPos(self.anchorSym) and anchorClose >= compareClose:
            return {"symbol": self.anchorSym, "side": "SELL"}

        return None
