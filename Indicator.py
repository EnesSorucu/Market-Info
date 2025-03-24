from operator import index
import pandas as pd
import pandas_ta as ta
import numpy as np
from database import StockData


class Indicator:
    def __init__(self, stock_c):
        self.stock_c = stock_c
        self.directory = f"datafolder/{stock_c}.csv"

    def load_data(self):
        # Load stock data from CSV file
        df = pd.read_csv(self.directory)
        df[["Close", "High", "Low", "Open", "Volume"]] = df[["Close", "High", "Low", "Open", "Volume"]].apply(pd.to_numeric, errors='coerce')
        return df

    def sma_indicator(self, period):
        # Calculate Simple Moving Average (SMA)
        df = self.load_data()
        if len(df) >= period:
            sma = df['Close'].rolling(window=period).mean()
            return sma

    def ema_indicator(self, period):
        # Calculate Exponential Moving Average (EMA)
        df = self.load_data()
        if len(df) >= period:
            ema = df['Close'].ewm(span=period, adjust=False).mean()
            return ema

    def rsi_indicator(self, period=14):
        # Calculate Relative Strength Index (RSI)
        df = self.load_data()
        if len(df) >= period:
            rsi = ta.rsi(df["Close"], period)
            return rsi

    def adx_indicator(self, period=14):
        # Calculate Average Directional Index (ADX)
        df = self.load_data()
        if len(df) >= period:
            cols = ["Close", "High", "Low"]
            df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
            adx = ta.trend.adx(df['High'], df['Low'], df['Close'], window=period)
            return adx["ADX_14"]

    def relative_vol(self, period=10):
        # Calculate Relative Volume compared to its moving average
        df = self.load_data()
        if len(df) >= period:
            df["average_vol"] = df["Volume"].rolling(window=period).mean()
            df["relative_vol"] = df["Volume"] / df["average_vol"]
            return df["relative_vol"]

    def golden_dead_cross(self):
        # Detect Golden Cross and Death Cross using SMA(50) and SMA(200)
        df = self.load_data()
        if len(df) > 200:
            df["sma50"] = self.sma_indicator(50)
            df["sma200"] = self.sma_indicator(200)

            df["Cross"] = np.where(df["sma50"] > df["sma200"], "Golden Cross", "Death Cross")

            cross_signals = df[["Date", "sma50", "sma200", "Cross"]]
            return cross_signals

    def macd_indicator(self):
        # Load stock data
        df = self.load_data()

        if len(df) > 26:
            df["ema12"] = self.ema_indicator(12) # Calculate 12-day EMA (short-term trend)
            df["ema26"] = self.ema_indicator(26) # Calculate 26-day EMA (long-term trend)

            df["macd"] = df["ema12"] - df["ema26"] # MACD line: Difference between 12-day EMA and 26-day EMA

            df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean() # Signal line: 9-day EMA of the MACD line

            df["histogram"] = df["macd"] - df["macd_signal"]             # Histogram: Difference between MACD line and Signal line

            df["signal"] = np.where(df["histogram"] > 0, "Positive Signal", "Negative Signal") # Generate buy/sell signals based on histogram values

            return df[["macd", "macd_signal", "histogram", "signal"]]

    def bollinger_bands(self):
        # Calculate Bollinger Bands (Upper, Lower, and Middle Bands)
        df = self.load_data()
        if len(df) >= 20:
            df["mid_band"] = self.sma_indicator(20)

            df["standard_dev"] = df['Close'].rolling(window=20).std()

            df["upper_band"] = df["mid_band"] + (2 * df["standard_dev"])
            df["lower_band"] = df["mid_band"] - (2 * df["standard_dev"])

            return df[['Close', "mid_band", "upper_band", "lower_band"]]
