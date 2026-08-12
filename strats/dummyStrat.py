from strats.baseStrat import BaseStrat


class DummyStrat(BaseStrat):
    """
    A strategy that buys every nth bar.
    """
    def __init__(self, buyEveryN=5, targetSym="SPY"):
        self.count = 0
        self.buyEveryN = buyEveryN
        self.targetSym = targetSym

    def genSig(self, snap, portfolio):
        self.count += 1
        if self.targetSym not in snap["bars"]:
            return None
        if portfolio.isFlat and self.count % self.buyEveryN == 0:
            return {"symbol": self.targetSym, "side": "BUY"}
        return None
