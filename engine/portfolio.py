class Portfolio:
    def __init__(self, initial_cash):
        self.cash = initial_cash
        self.holdings = 0
        self.last_price = 0

    def execute_signal(self, signal, bar):
        price = bar["close"]
        self.last_price = price

        if signal == "BUY" and self.cash > price:
            shares_to_buy = int(self.cash // price)
            self.holdings += shares_to_buy
            self.cash -= shares_to_buy * price

        elif signal == "SELL" and self.holdings > 0:
            self.cash += self.holdings * price
            self.holdings = 0

    @property
    def market_value(self):
        return self.cash + (self.holdings * self.last_price)
