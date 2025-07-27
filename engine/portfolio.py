class Portfolio:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.holdings = 0
        self.last_price = 0
        self.open_trades = []  # list of open buy trades (FIFO)
        self.closed_trades = []  # list of dicts with pnl, entry/exit info

    def execute_signal(self, signal, bar):
        price = bar["close"]
        self.last_price = price

        if signal == "BUY" and self.cash >= price:
            shares_to_buy = int(self.cash // price)
            if shares_to_buy > 0:
                self.cash -= shares_to_buy * price
                self.holdings += shares_to_buy
                self.open_trades.append({
                    "entry_price": price,
                    "shares": shares_to_buy,
                    "entry_time": bar["date"]
                })

        elif signal == "SELL" and self.holdings > 0:
            proceeds = self.holdings * price
            self.cash += proceeds

            # Close all open trades
            for trade in self.open_trades:
                pnl = (price - trade["entry_price"]) * trade["shares"]
                self.closed_trades.append({
                    "entry_time": trade["entry_time"],
                    "exit_time": bar["date"],
                    "entry_price": trade["entry_price"],
                    "exit_price": price,
                    "shares": trade["shares"],
                    "pnl": pnl
                })

            self.open_trades = []
            self.holdings = 0

    @property
    def market_value(self):
        return self.cash + self.holdings * self.last_price