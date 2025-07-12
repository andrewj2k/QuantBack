class ExecutionHandler:
    """
    Simulates orders based on signal.
    """

    def __init__(self):
        pass

    def execute_trade(self, signal, price):
        """
        Simulates trade fill.
        signal: 'BUY' or 'SELL'
        price: price at fill(assume close or mid)
        Returns: trade dict with keys ['timestamp', 'side', 'price', 'size']
        """
        pass
