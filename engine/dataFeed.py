import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataFeed:
    def __init__(self, source, symbols, startDate, endDate):
        logger.info(f"Loading data from {source}...")

        try:
            df = pd.read_csv(source)
            df["date"] = pd.to_datetime(df["date"])

            df = df[
                (df["date"] >= pd.to_datetime(startDate)) &
                (df["date"] <= pd.to_datetime(endDate))
            ]
            df = df[df["symbol"].isin(symbols)].copy()

            # For relative-value work, we want dates where every symbol is present.
            counts = df.groupby("date")["symbol"].nunique()
            sharedDates = counts[counts == len(symbols)].index
            df = df[df["date"].isin(sharedDates)].copy()
            df = df.sort_values(["date", "symbol"]).reset_index(drop=True)

            self.df = df
            self.symbols = symbols
            self.dates = list(df["date"].drop_duplicates())
            self.idx = 0

            logger.info(
                f"Loaded {len(self.df)} rows across {len(self.symbols)} symbols and {len(self.dates)} dates"
            )

        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            raise

    def nextSnap(self):
        if self.idx < len(self.dates):
            date = self.dates[self.idx]
            dayDf = self.df[self.df["date"] == date]
            self.idx += 1

            bars = {}
            for _, row in dayDf.iterrows():
                bars[row["symbol"]] = {
                    "date": row["date"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                }

            return {
                "date": date,
                "bars": bars,
            }
        return None
