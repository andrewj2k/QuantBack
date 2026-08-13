import logging

logger = logging.getLogger(__name__)


class Exec:
    """
    Simulates market order execution.
    """

    def __init__(self, slipBps=0.0, feePerOrder=0.0):
        self.tradeId = 0
        self.slipBps = slipBps
        self.feePerOrder = feePerOrder

    def _slipPrice(self, side, midPrice):
        """
        Apply adverse slippage:
        - buys pay a little more than the observed price
        - sells receive a little less than the observed price
        """
        slip = self.slipBps / 10000.0
        if side == "BUY":
            return midPrice * (1 + slip)
        if side == "SELL":
            return midPrice * (1 - slip)
        return midPrice

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

        fillPrice = self._slipPrice(order["side"], price)
        self.tradeId += 1
        trade = {
            "id": self.tradeId,
            "timestamp": ts,
            "symbol": order["symbol"],
            "side": order["side"],
            "rawPrice": price,
            "price": fillPrice,
            "size": 1,  # Placeholder size
            "slipBps": self.slipBps,
            "fee": self.feePerOrder,
            "meta": order.get("meta", {}),
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
