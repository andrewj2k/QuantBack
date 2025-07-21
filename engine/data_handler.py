import pandas as pd
import logging
from typing import Optional

# Set up logging for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DataHandler:
    """
    Provides OHLCV market data one bar at a time from a CSV file.
    """

    def __init__(self, source, start_date, end_date):
        """
        Initializes the data handler by loading a CSV and preparing an iterator.

        Parameters:
        - source (str): Path to the OHLCV CSV file with these columns:
            ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        - start_date (str): YYYY-MM-DD string to filter start of data
        - end_date (str): YYYY-MM-DD string to filter end of data
        """
        logger.info(f"Loading data from {source}...")

        try:
            self.df = pd.read_csv(source, parse_dates=["Date"])
        except FileNotFoundError:
            logger.error(f"File not found: {source}")
            raise
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise

        # Normalize columns
        self.df.rename(columns=str.lower, inplace=True)

        # Check columns
        required_cols = {"open", "high", "low", "close", "volume", "date"}
        if not required_cols.issubset(set(self.df.columns).union(self.df.index.names)):
            raise ValueError(f"CSV missing required columns: {required_cols - set(self.df.columns)}")

        # Set index
        self.df.set_index("date", inplace=True)

        # Retain OHLCV columns
        self.df = self.df[["open", "high", "low", "close", "volume"]]

        # 🔁 Filter by date range
        if start_date:
            self.df = self.df.loc[start_date:]
            logger.info(f"Trimmed start date to {start_date}")
        if end_date:
            self.df = self.df.loc[:end_date]
            logger.info(f"Trimmed end date to {end_date}")

        # Log remaining bars
        logger.info(f"{len(self.df)} bars available after trimming")

        # Create iterator
        self.bar_iter = self.df.iterrows()

    def get_next_bar(self):
        """
        Returns the next OHLCV bar as a dictionary.

        Output:
        {
            "timestamp": pd.Timestamp,
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float
        }
        """
        try:
            timestamp, row = next(self.bar_iter)

            logger.info(f"Returning bar at {timestamp.date()} | Close: {row['close']}")

            return {
                "timestamp": timestamp,
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"]
            }

        except StopIteration:
            logger.info("No more bars available. End of dataset reached.")
            return None

