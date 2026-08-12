from collections import deque
from statistics import mean, pstdev

from strats.baseStrat import BaseStrat


class PairStrat(BaseStrat):
    """
    First real spread strategy.

    We use a simple raw spread for learning:
        spread = closeA - closeB

    Then we compute a rolling z-score and trade the relative move:
    - if spread is too low, buy A / sell B
    - if spread is too high, sell A / buy B
    - exit when the spread mean reverts toward zero
    """

    def __init__(self, symA="SPY", symB="IVV", lookback=20, entryZ=1.5, exitZ=0.3):
        self.symA = symA
        self.symB = symB
        self.lookback = lookback
        self.entryZ = entryZ
        self.exitZ = exitZ
        self.spreads = deque(maxlen=lookback)

    def genSig(self, snap, portfolio):
        bars = snap["bars"]
        if self.symA not in bars or self.symB not in bars:
            return None

        spread = bars[self.symA]["close"] - bars[self.symB]["close"]
        self.spreads.append(spread)

        if len(self.spreads) < self.lookback:
            return None

        spreadMean = mean(self.spreads)
        spreadStd = pstdev(self.spreads)
        if spreadStd == 0:
            return None

        zScore = (spread - spreadMean) / spreadStd

        if portfolio.isFlat:
            if zScore < -self.entryZ:
                return [
                    {"symbol": self.symA, "side": "BUY"},
                    {"symbol": self.symB, "side": "SELL"},
                ]
            if zScore > self.entryZ:
                return [
                    {"symbol": self.symA, "side": "SELL"},
                    {"symbol": self.symB, "side": "BUY"},
                ]

        if portfolio.isPairOpen and abs(zScore) < self.exitZ:
            return portfolio.closeOrders()

        return None
