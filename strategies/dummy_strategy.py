from strategies.base_strategy import BaseStrategy

class DummyStrategy(BaseStrategy):
    """
    A strategy that buys every nth bar.
    """
    def __init__(self, buy_every_n=5):
        self.counter = 0
        self.buy_every_n = buy_every_n

    def generate_signal(self, bar):
        self.counter += 1
        if self.counter % self.buy_every_n == 0:
            return "BUY"
        return None