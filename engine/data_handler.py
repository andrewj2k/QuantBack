import pandas as pd
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DataHandler:
    """
    Provides OHLCV market data one bar at a time from a CSV file.
    """

    def __init__(self, source, start_date, end_date):
        logger.info(f"Loading data from {source}...")

        try:
            # Skip 3 junk rows and assign real column names
            self.df = pd.read_csv(
                source,
                skiprows=3,
                names=["Date", "Close", "High", "Low", "Open", "Volume"],
                header=None
            )

            self.df["Date"] = pd.to_datetime(self.df["Date"], errors="raise")
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise

        # Filter by date range
        self.df = self.df[
            (self.df["Date"] >= pd.to_datetime(start_date)) &
            (self.df["Date"] <= pd.to_datetime(end_date))
        ]

        self.df.reset_index(drop=True, inplace=True)
        self.bar_iter = self.df.iterrows()

        logger.info(f"Loaded {len(self.df)} bars from {source}")

    def get_next_bar(self):
        try:
            _, row = next(self.bar_iter)
            logger.info(f"Returning bar at {row['Date'].date()} | Close: {row['Close']}")
            return {
                "timestamp": row["Date"],
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"]
            }
        except StopIteration:
            logger.info("No more bars available.")
            return None