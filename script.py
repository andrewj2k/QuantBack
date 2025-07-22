import yfinance as yf
import pandas as pd
import os

# Download daily SPY data for 2023 (no need for auto_adjust since we're ignoring Adj Close)
spy = yf.download("SPY", start="2023-01-01", end="2023-12-31", interval="1d")

# Reset index so 'Date' becomes a column
spy.reset_index(inplace=True)

# Select only the needed columns
spy = spy[["Date", "Open", "High", "Low", "Close", "Volume"]]

# Ensure output directory exists
os.makedirs("data", exist_ok=True)

# Write CSV with two dummy rows to match skiprows=2 in your DataHandler
with open("data/SPY.csv", "w") as f:
    f.write("Dummy row 1\n")
    f.write("Dummy row 2\n")
    spy.to_csv(f, index=False)