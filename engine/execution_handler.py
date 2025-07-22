import logging

logger = logging.getLogger(__name__)

class ExecutionHandler:
    """
    Simulates market order execution.
    """

    def __init__(self):
        self.trade_id = 0

    def execute_trade(self, signal, price, timestamp):
        """
        Simulates execution and returns trade info.
        signal: 'BUY' or 'SELL'
        price: assumed fill price (usually close)
        timestamp: time of the bar
        """
        if signal not in ["BUY", "SELL"]:
            return None

        self.trade_id += 1
        trade = {
            "id": self.trade_id,
            "timestamp": timestamp,
            "side": signal,
            "price": price,
            "size": 1  # Placeholder size 
        }

        logger.info(f"Executed trade {trade}")
        return trade
