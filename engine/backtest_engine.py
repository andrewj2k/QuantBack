class BacktestEngine:
    """
    Orchestrates the backtest
    """

    def __init__(self, data_handler, strategy, execution_handler, portfolio, evaluator):
        self.data = data_handler
        self.strategy = strategy

    def run(self):
        """
        Main loop:
        1. Get bar
        2. Generate signal
        3. Execute trade
        4. Update portfolio
        5. Results
        """
        bar = self.data.get_next_bar()
        while bar:
            signal = self.strategy.generate_signal(bar)
            if signal:
                print(f"Signal at {bar['timestamp'].date()}: {signal}")
            bar = self.data.get_next_bar()