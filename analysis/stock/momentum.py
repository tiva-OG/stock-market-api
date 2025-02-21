# 2️⃣ Momentum Analysis (Trend Strength & Reversals)
import pandas as pd

"""
A. RSI (Relative Strength Index)
~ Use Case: Identifies overbought/oversold conditions.
~ Implementation:
	~~ RSI = 100 - (100 / (1 + RS)), where RS = (Avg Gain / Avg Loss) over 14 days.

🔹 Trading Signals:
~ RSI > 70 → Overbought (Potential Sell)
~ RSI < 30 → Oversold (Potential Buy)
~ RSI Divergence → If RSI moves opposite to price, trend reversal likely
"""


def calculate_rsi(data: pd.DataFrame, period: int = 14):
	# Relative Strength Index (RSI)
	delta = data["Close"].diff()
	gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
	loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
	rs = gain / loss
	rsi = 100 - (100 / (1 + rs))
	return rsi


"""
B. MACD (Moving Average Convergence Divergence)
~ Use Case: Identifies momentum shifts and confirms trends.
~ Implementation:
	~~ MACD Line = 12-day EMA – 26-day EMA
	~~ Signal Line = 9-day EMA of MACD
	
🔹 Trading Signals:
~ MACD crosses above Signal Line → Bullish trend
~ MACD crosses below Signal Line → Bearish trend
~ MACD Divergence → If MACD moves opposite to price, trend reversal likely
"""


def calculate_macd(data: pd.DataFrame, short_period: int = 12, long_period: int = 26, signal_period: int = 9):
	# Moving Average Convergence Divergence (MACD)
	short_ema = data["Close"].ewm(span=short_period, adjust=False).mean()
	long_ema = data["Close"].ewm(span=long_period, adjust=False).mean()
	macd = short_ema - long_ema
	signal = macd.ewm(span=signal_period, adjust=False).mean()
	return macd, signal
