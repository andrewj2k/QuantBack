from strategies.base_strategy import BaseStrategy

class DummyStrategy(BaseStrategy):
    """
    A strategy that buys every 5th bar.
    """
    def __init__(self):
        self.counter = 0

    def generate_signal(self, bar):
        self.counter += 1
        if self.counter % 5 == 0:
            return "BUY"
        return None