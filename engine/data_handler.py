import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DataHandler:
    def __init__(self, source, start_date, end_date):
        logger.info(f"Loading data from {source}...")

        try:
            df = pd.read_csv(source, skiprows=2)  # Row 3 becomes header
            df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d")

            # Filter by date
            df = df[
                (df["Date"] >= pd.to_datetime(start_date)) &
                (df["Date"] <= pd.to_datetime(end_date))
            ]

            df.reset_index(drop=True, inplace=True)
            self.df = df
            self.current_index = 0

            logger.info(f"Loaded {len(self.df)} bars from {source}")

        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise

    def get_next_bar(self):
        if self.current_index < len(self.df):
            bar = self.df.iloc[self.current_index]
            self.current_index += 1
            logger.info(f"Returning bar at {bar['Date']} | Close: {bar['Close']}")
            return bar
        return None