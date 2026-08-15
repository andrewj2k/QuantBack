from pathlib import Path

import pandas as pd


CSV_PATH = Path("data/prices.csv")
PARQUET_PATH = Path("data/prices.parquet")
REQ_COLS = ["date", "symbol", "open", "high", "low", "close", "volume"]


def main():
    df = pd.read_csv(CSV_PATH)
    missing = [col for col in REQ_COLS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[REQ_COLS].copy()
    df["date"] = pd.to_datetime(df["date"])
    PARQUET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PARQUET_PATH, index=False)
    print(f"Saved {len(df)} rows to {PARQUET_PATH}")


if __name__ == "__main__":
    main()
