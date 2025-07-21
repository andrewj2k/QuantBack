import pandas as pd
import logging

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
        - source (str): Path to the OHLCV CSV file with at least these columns:
          ['Price' (datetime), 'Open', 'High', 'Low', 'Close', 'Volume']
        - start_date (str or None): Optional start date filter (e.g., '2020-01-01')
        - end_date (str or None): Optional end date filter (e.g., '2023-01-01')
        """
        logger.info(f"Loading data from {source}...")

        try:
            # Skip first 2 rows, parse "Price" as datetime
            self.df = pd.read_csv(source, skiprows=2, parse_dates=["Price"])
            self.df.rename(columns={"Price": "date"}, inplace=True)
        except FileNotFoundError:
            logger.error(f"File not found: {source}")
            raise
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise

        # Normalize column names
        self.df.rename(columns=str.lower, inplace=True)

        # Filter date range
        if start_date:
            self.df = self.df[self.df["date"] >= pd.to_datetime(start_date)]
        if end_date:
            self.df = self.df[self.df["date"] <= pd.to_datetime(end_date)]

        # Ensure required columns exist
        required_cols = {"open", "high", "low", "close", "volume", "date"}
        if not required_cols.issubset(set(self.df.columns)):
            raise ValueError(f"CSV missing required columns: {required_cols - set(self.df.columns)}")

        # Set date as index
        self.df.set_index("date", inplace=True)

        # Retain only essential columns
        self.df = self.df[["open", "high", "low", "close", "volume"]]

        # Create an iterator over the bars
        self.bar_iter = self.df.iterrows()

        logger.info(f"Loaded {len(self.df)} bars from {source}")

    def get_next_bar(self):
        """
        Returns the next bar of OHLCV data as a dictionary.
        Returns None if all data has been consumed.

        Output Example:
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