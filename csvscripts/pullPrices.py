from pathlib import Path

import pandas as pd
import yfinance as yf


SYMS = ["SPY", "IVV", "QQQ"]
START = "2023-01-01"
END = "2023-12-31"
OUT_PATH = Path("data/prices.csv")


def pullOne(sym, start, end):
    """
    Pull one symbol and normalize it into the flat schema the backtester wants.

    We add a symbol column explicitly because multi-asset backtests are easier to
    reason about when each row says both "what date" and "what asset".
    """
    df = yf.download(sym, start=start, end=end, interval="1d", auto_adjust=False)
    df = df.reset_index()
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    df["symbol"] = sym
    df.columns = ["date", "open", "high", "low", "close", "volume", "symbol"]
    return df[["date", "symbol", "open", "high", "low", "close", "volume"]]


def main():
    frames = []
    for sym in SYMS:
        print(f"Pulling {sym}...")
        frames.append(pullOne(sym, START, END))

    prices = pd.concat(frames, ignore_index=True)
    prices = prices.sort_values(["date", "symbol"]).reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    prices.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(prices)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
