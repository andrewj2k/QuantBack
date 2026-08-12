class Portfolio:
    def __init__(self, initCash):
        self.cash = initCash
        self.lastPrices = {}
        self.pos = {}
        self.openPkg = []
        self.closedTrades = []

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
        unitCash = self.cash / max(len(trades), 1)

        for trade in trades:
            sym = trade["symbol"]
            side = trade["side"]
            price = trade["price"]
            shares = max(int(unitCash // price), 1)
            signedQty = shares if side == "BUY" else -shares

            self.cash -= signedQty * price
            self.pos[sym] = self.pos.get(sym, 0) + signedQty
            pkg.append({
                "symbol": sym,
                "side": side,
                "entry_price": price,
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
            self.cash += qty * trade["price"]
            self.pos[sym] = 0

            if openLeg["side"] == "BUY":
                pnl = (trade["price"] - openLeg["entry_price"]) * openLeg["shares"]
            else:
                pnl = (openLeg["entry_price"] - trade["price"]) * openLeg["shares"]

            self.closedTrades.append({
                "symbol": sym,
                "entry_time": openLeg["entry_time"],
                "exit_time": ts,
                "entry_price": openLeg["entry_price"],
                "exit_price": trade["price"],
                "shares": openLeg["shares"],
                "side": openLeg["side"],
                "pnl": pnl,
            })

        self.pos = {sym: qty for sym, qty in self.pos.items() if qty != 0}
        self.openPkg = []

    def hasPos(self, sym):
        return self.pos.get(sym, 0) != 0

    def closeOrders(self):
        orders = []
        for sym, qty in self.pos.items():
            side = "SELL" if qty > 0 else "BUY"
            orders.append({"symbol": sym, "side": side})
        return orders

    @property
    def isFlat(self):
        return len(self.pos) == 0

    @property
    def isPairOpen(self):
        return len(self.pos) == 2

    @property
    def mktVal(self):
        posVal = 0
        for sym, qty in self.pos.items():
            posVal += qty * self.lastPrices.get(sym, 0)
        return self.cash + posVal
