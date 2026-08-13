class Portfolio:
    def __init__(self, initCash, maxPkgFrac=1.0, maxDollarPerLeg=None):
        self.cash = initCash
        self.lastPrices = {}
        self.pos = {}
        self.openPkg = []
        self.closedTrades = []
        self.maxPkgFrac = maxPkgFrac
        self.maxDollarPerLeg = maxDollarPerLeg

    def markToMkt(self, snap):
        for sym, bar in snap["bars"].items():
            self.lastPrices[sym] = bar["close"]

    def onTrades(self, trades, snap):
        if not trades:
            return

        if self.isFlat:
            self._openPkg(trades, snap["date"])
            return

        self._closePkg(trades, snap["date"])

    def _openPkg(self, trades, ts):
        pkg = []
        pkgBudget = self.cash * self.maxPkgFrac
        unitBudget = pkgBudget / max(len(trades), 1)

        if self.maxDollarPerLeg is not None:
            unitBudget = min(unitBudget, self.maxDollarPerLeg)

        for trade in trades:
            sym = trade["symbol"]
            side = trade["side"]
            price = trade["price"]
            shares = max(int(unitBudget // price), 1)
            signedQty = shares if side == "BUY" else -shares
            fee = trade.get("fee", 0.0)

            self.cash -= signedQty * price
            self.cash -= fee
            self.pos[sym] = self.pos.get(sym, 0) + signedQty
            pkg.append({
                "symbol": sym,
                "side": side,
                "pairSide": trade.get("meta", {}).get("pairSide"),
                "entry_z": trade.get("meta", {}).get("entryZ"),
                "entry_spread": trade.get("meta", {}).get("entrySpread"),
                "entry_raw_price": trade.get("rawPrice"),
                "entry_price": price,
                "entry_fee": fee,
                "shares": shares,
                "entry_time": ts,
            })

        self.openPkg = pkg

    def _closePkg(self, trades, ts):
        openBySym = {leg["symbol"]: leg for leg in self.openPkg}

        for trade in trades:
            sym = trade["symbol"]
            if sym not in openBySym:
                continue

            openLeg = openBySym[sym]
            qty = self.pos.get(sym, 0)
            fee = trade.get("fee", 0.0)
            self.cash += qty * trade["price"]
            self.cash -= fee
            self.pos[sym] = 0

            if openLeg["side"] == "BUY":
                grossPnl = (trade["price"] - openLeg["entry_price"]) * openLeg["shares"]
            else:
                grossPnl = (openLeg["entry_price"] - trade["price"]) * openLeg["shares"]

            netPnl = grossPnl - openLeg.get("entry_fee", 0.0) - fee

            self.closedTrades.append({
                "symbol": sym,
                "entry_time": openLeg["entry_time"],
                "exit_time": ts,
                "entry_raw_price": openLeg.get("entry_raw_price"),
                "entry_price": openLeg["entry_price"],
                "exit_raw_price": trade.get("rawPrice"),
                "exit_price": trade["price"],
                "shares": openLeg["shares"],
                "side": openLeg["side"],
                "pairSide": openLeg.get("pairSide"),
                "entry_z": openLeg.get("entry_z"),
                "exit_z": trade.get("meta", {}).get("exitZ"),
                "entry_spread": openLeg.get("entry_spread"),
                "exit_spread": trade.get("meta", {}).get("exitSpread"),
                "hold_bars": trade.get("meta", {}).get("holdBars"),
                "exit_reason": trade.get("meta", {}).get("exitReason"),
                "entry_fee": openLeg.get("entry_fee", 0.0),
                "exit_fee": fee,
                "gross_pnl": grossPnl,
                "pnl": netPnl,
            })

        self.pos = {sym: qty for sym, qty in self.pos.items() if qty != 0}
        self.openPkg = []

    def hasPos(self, sym):
        return self.pos.get(sym, 0) != 0

    def closeOrders(self, meta=None):
        orders = []
        for sym, qty in self.pos.items():
            side = "SELL" if qty > 0 else "BUY"
            orders.append({"symbol": sym, "side": side, "meta": meta or {}})
        return orders

    @property
    def isFlat(self):
        return len(self.pos) == 0

    @property
    def isPairOpen(self):
        return len(self.pos) == 2

    @property
    def pkgNotional(self):
        notional = 0.0
        for leg in self.openPkg:
            notional += leg["entry_price"] * leg["shares"]
        return notional

    @property
    def pkgPnl(self):
        pnl = 0.0
        for leg in self.openPkg:
            curPrice = self.lastPrices.get(leg["symbol"], leg["entry_price"])
            if leg["side"] == "BUY":
                pnl += (curPrice - leg["entry_price"]) * leg["shares"]
            else:
                pnl += (leg["entry_price"] - curPrice) * leg["shares"]
            pnl -= leg.get("entry_fee", 0.0)
        return pnl

    @property
    def pkgRet(self):
        if not self.openPkg or self.pkgNotional == 0:
            return 0.0
        return self.pkgPnl / self.pkgNotional

    @property
    def mktVal(self):
        posVal = 0
        for sym, qty in self.pos.items():
            posVal += qty * self.lastPrices.get(sym, 0)
        return self.cash + posVal
