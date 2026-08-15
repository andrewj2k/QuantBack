import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataFeed:
    REQ_COLS = ["date", "symbol", "open", "high", "low", "close", "volume"]

    def __init__(self, source, symbols, startDate, endDate):
        logger.info(f"Loading data from {source}...")

        try:
            df = self._loadRaw(source)
            df = self._normalize(df)

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
            logger.error(f"Failed to read data: {e}")
            raise

    def _loadRaw(self, source):
        ext = Path(source).suffix.lower()
        if ext == ".csv":
            return self._loadCsv(source)
        if ext == ".parquet":
            return self._loadParquet(source)
        raise ValueError(f"Unsupported data file type: {ext}")

    def _loadCsv(self, source):
        return pd.read_csv(source)

    def _loadParquet(self, source):
        return pd.read_parquet(source)

    def _normalize(self, df):
        missing = [col for col in self.REQ_COLS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df = df[self.REQ_COLS].copy()
        df["date"] = pd.to_datetime(df["date"])
        return df

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
