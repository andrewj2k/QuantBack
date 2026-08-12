import logging

logger = logging.getLogger(__name__)


class Exec:
    """
    Simulates market order execution.
    """

    def __init__(self):
        self.tradeId = 0

    def fill(self, order, price, ts):
        """
        Simulates execution and returns trade info.
        order: dict like {"symbol": "SPY", "side": "BUY"}
        price: assumed fill price (usually close)
        timestamp: time of the bar
        """
        if not order:
            return None
        if order.get("side") not in ["BUY", "SELL"]:
            return None

        self.tradeId += 1
        trade = {
            "id": self.tradeId,
            "timestamp": ts,
            "symbol": order["symbol"],
            "side": order["side"],
            "price": price,
            "size": 1,  # Placeholder size
        }

        logger.info(f"Executed trade {trade}")
        return trade

    def fillOrders(self, orders, snap):
        trades = []
        for order in orders:
            bar = snap["bars"][order["symbol"]]
            trade = self.fill(order, price=bar["close"], ts=snap["date"])
            if trade:
                trades.append(trade)
        return trades
