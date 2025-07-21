import pandas as pd
import logging

# Set up logging for this module
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DataHandler:
    """
    Provides OHLCV market data one bar at a time from a CSV file.
    """

    def __init__(self, source, start_date=None, end_date=None):
        """
        Initializes the data handler by loading a CSV and preparing an iterator.

        Parameters:
        - source (str): Path to the OHLCV CSV file with this column layout:
          ['Date', <open>, <high>, <low>, <close>, <volume>]
        - start_date (str or None): Optional start date filter (e.g., '2020-01-01')
        - end_date (str or None): Optional end date filter (e.g., '2023-01-01')
        """
        logger.info(f"Loading data from {source}...")

        try:
            # Skip first 2 rows and parse the date column
            self.df = pd.read_csv(source, skiprows=2, parse_dates=["Date"])
        except FileNotFoundError:
            logger.error(f"File not found: {source}")
            raise
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise

        # Rename columns to standard names
        self.df.columns = ["date", "open", "high", "low", "close", "volume"]

        # Filter by date range if provided
        if start_date:
            self.df = self.df[self.df["date"] >= pd.to_datetime(start_date)]
        if end_date:
            self.df = self.df[self.df["date"] <= pd.to_datetime(end_date)]

        # Set index to datetime
        self.df.set_index("date", inplace=True)

        # Keep only required columns
        self.df = self.df[["open", "high", "low", "close", "volume"]]

        # Create an iterator for step-by-step access
        self.bar_iter = self.df.iterrows()

        logger.info(f"Loaded {len(self.df)} bars from {source}")

    def get_next_bar(self):
        """
        Returns the next bar of OHLCV data as a dictionary.
        Returns None if all data has been consumed.

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