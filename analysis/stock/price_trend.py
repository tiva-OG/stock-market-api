# 1️⃣ Price Trend Analysis (Trend-Following Strategies)
import pandas as pd

"""
A. Moving Averages (SMA & EMA)
~ Use Case: Identify trends and smooth out price fluctuations.
~ Implementation:
	~~ Short-term SMA (e.g., 10-day) → Detect quick trends
	~~ Long-term SMA (e.g., 50-day, 200-day) → Identify overall trend
	~~ EMA (Exponential Moving Average) → Reacts faster to recent prices
	
🔹 Trading Signals:
~ Price above SMA/EMA → Bullish trend
~ Price below SMA/EMA → Bearish trend
~ Golden Cross (SMA-50 crosses SMA-200 upward) → Buy Signal
~ Death Cross (SMA-50 crosses SMA-200 downward) → Sell Signal
"""


def calculate_sma(data: pd.DataFrame, period: int = 20):
	# Simple Moving Average (SMA)
	return data["Close"].rolling(window=period).mean()


def calculate_ema(data: pd.DataFrame, period: int = 20):
	# Exponential Moving Average (EMA)
	return data["Close"].ewm(span=period, adjust=False).mean()


"""
B. Bollinger Bands
~ Use Case: Measure stock volatility and detect breakouts.
~ Implementation:
	~~ Middle Band = 20-day SMA
	~~ Upper Band = SMA + (2 × Standard Deviation)
	~~ Lower Band = SMA − (2 × Standard Deviation)
	
🔹 Trading Signals:
~ Price touches Upper Band → Overbought (potential reversal or breakout)
~ Price touches Lower Band → Oversold (potential upward reversal)
"""
