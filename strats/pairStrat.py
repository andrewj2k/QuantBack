from collections import deque
from math import log

from engine.fastStats import calcBeta, calcSpreadWindowStats, pickBackend
from strats.baseStrat import BaseStrat


class PairStrat(BaseStrat):
    """
    First real spread strategy.

    We use a log spread for learning:
        spread = log(closeA) - log(closeB)

    Then we compute a rolling z-score and trade the relative move:
    - if spread is too low, buy A / sell B
    - if spread is too high, sell A / buy B
    - exit when the spread mean reverts toward zero
    """

    def __init__(
        self,
        symA="SPY",
        symB="IVV",
        spreadMode="log",
        hedgeMode="unit",
        lookback=20,
        entryZ=1.5,
        exitZ=0.3,
        stopLossPct=0.005,
        maxHoldBars=20,
        mathBackend="auto",
    ):
        self.symA = symA
        self.symB = symB
        self.spreadMode = spreadMode
        self.hedgeMode = hedgeMode
        self.lookback = lookback
        self.entryZ = entryZ
        self.exitZ = exitZ
        self.stopLossPct = stopLossPct
        self.maxHoldBars = maxHoldBars
        self.mathBackend = pickBackend(mathBackend)
        self.spreads = deque(maxlen=lookback)
        self.logA = deque(maxlen=lookback)
        self.logB = deque(maxlen=lookback)
        self.signalLog = []
        self.state = "flat"
        self.holdBars = 0
        self.hedgeRatio = 1.0

    def _calcBeta(self):
        return calcBeta(self.logB, self.logA, backend=self.mathBackend)

    def _updateHedgeRatio(self):
        if self.hedgeMode == "unit":
            self.hedgeRatio = 1.0
        elif self.hedgeMode == "staticBeta":
            # Estimate beta once after the first warmup window and keep it fixed.
            if len(self.logA) == self.lookback and self.hedgeRatio == 1.0:
                self.hedgeRatio = self._calcBeta()
        else:
            raise ValueError(f"Unsupported hedge mode: {self.hedgeMode}")

    def _calcSpread(self, bars):
        logA = log(bars[self.symA]["close"])
        logB = log(bars[self.symB]["close"])

        if self.spreadMode == "log":
            return logA - self.hedgeRatio * logB
        if self.spreadMode == "raw":
            priceA = bars[self.symA]["close"]
            priceB = bars[self.symB]["close"]
            return priceA - priceB

        raise ValueError(f"Unsupported spread mode: {self.spreadMode}")

    def _logRow(self, snap, spread, spreadMean, spreadStd, zScore, action, portfolio=None):
        self.signalLog.append({
            "date": snap["date"],
            "symA": self.symA,
            "symB": self.symB,
            "spreadMode": self.spreadMode,
            "hedgeMode": self.hedgeMode,
            "mathBackend": self.mathBackend,
            "hedgeRatio": self.hedgeRatio,
            "spread": spread,
            "spreadMean": spreadMean,
            "spreadStd": spreadStd,
            "zScore": zScore,
            "state": self.state,
            "holdBars": self.holdBars,
            "pkgPnl": None if portfolio is None else portfolio.pkgPnl,
            "pkgRet": None if portfolio is None else portfolio.pkgRet,
            "action": action,
        })

    def genSig(self, snap, portfolio):
        bars = snap["bars"]
        if self.symA not in bars or self.symB not in bars:
            return None

        self.logA.append(log(bars[self.symA]["close"]))
        self.logB.append(log(bars[self.symB]["close"]))
        self._updateHedgeRatio()
        spread = self._calcSpread(bars)

        if len(self.logA) < self.lookback:
            self._logRow(snap, spread, None, None, None, "warmup", portfolio)
            return None

        self.spreads.append(spread)
        spread, spreadMean, spreadStd, zScore = calcSpreadWindowStats(
            self.spreads,
            backend=self.mathBackend,
        )
        if zScore is None:
            self._logRow(snap, spread, spreadMean, spreadStd, None, "flat-std", portfolio)
            return None

        if portfolio.isFlat:
            self.holdBars = 0
            if zScore < -self.entryZ:
                self.state = "longSpread"
                self._logRow(snap, spread, spreadMean, spreadStd, zScore, "enterLongSpread", portfolio)
                return [
                    {
                        "symbol": self.symA,
                        "side": "BUY",
                        "meta": {
                            "pairSide": "longSpread",
                            "entryZ": zScore,
                            "entrySpread": spread,
                        },
                    },
                    {
                        "symbol": self.symB,
                        "side": "SELL",
                        "meta": {
                            "pairSide": "longSpread",
                            "entryZ": zScore,
                            "entrySpread": spread,
                        },
                    },
                ]
            if zScore > self.entryZ:
                self.state = "shortSpread"
                self._logRow(snap, spread, spreadMean, spreadStd, zScore, "enterShortSpread", portfolio)
                return [
                    {
                        "symbol": self.symA,
                        "side": "SELL",
                        "meta": {
                            "pairSide": "shortSpread",
                            "entryZ": zScore,
                            "entrySpread": spread,
                        },
                    },
                    {
                        "symbol": self.symB,
                        "side": "BUY",
                        "meta": {
                            "pairSide": "shortSpread",
                            "entryZ": zScore,
                            "entrySpread": spread,
                        },
                    },
                ]

        if portfolio.isPairOpen:
            self.holdBars += 1

        if portfolio.isPairOpen and portfolio.pkgRet <= -self.stopLossPct:
            self._logRow(snap, spread, spreadMean, spreadStd, zScore, "stopLossExit", portfolio)
            closeOrders = portfolio.closeOrders({
                "exitZ": zScore,
                "exitSpread": spread,
                "pairSide": self.state,
                "exitReason": "stopLoss",
                "holdBars": self.holdBars,
            })
            self.state = "flat"
            self.holdBars = 0
            return closeOrders

        if portfolio.isPairOpen and self.holdBars >= self.maxHoldBars:
            self._logRow(snap, spread, spreadMean, spreadStd, zScore, "maxHoldExit", portfolio)
            closeOrders = portfolio.closeOrders({
                "exitZ": zScore,
                "exitSpread": spread,
                "pairSide": self.state,
                "exitReason": "maxHold",
                "holdBars": self.holdBars,
            })
            self.state = "flat"
            self.holdBars = 0
            return closeOrders

        if portfolio.isPairOpen and abs(zScore) < self.exitZ:
            self._logRow(snap, spread, spreadMean, spreadStd, zScore, "meanRevertExit", portfolio)
            closeOrders = portfolio.closeOrders({
                "exitZ": zScore,
                "exitSpread": spread,
                "pairSide": self.state,
                "exitReason": "meanRevert",
                "holdBars": self.holdBars,
            })
            self.state = "flat"
            self.holdBars = 0
            return closeOrders

        self._logRow(snap, spread, spreadMean, spreadStd, zScore, "hold", portfolio)

        return None
