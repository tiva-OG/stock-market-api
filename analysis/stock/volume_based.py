# 4️⃣ Volume-Based Analysis (Confirming Price Moves)
import pandas as pd

"""
A. OBV (On-Balance Volume)
~ Use Case: Tracks whether volume supports price moves.

🔹 Trading Insight:
~ Price rising + OBV rising → Strong uptrend
~ Price rising + OBV falling → Weak uptrend, potential reversal
"""


def calculate_obv(data: pd.DataFrame):
	# On-Balance Volume (OBV)
	obv = [0]  # first value is 0
	for i in range(1, len(data)):
		if data["Close"].iloc[i] > data["Close"].iloc[i - 1]:
			obv.append(obv[-1] + data["Volume"].iloc[i])
		elif data["Close"].iloc[i] < data["Close"].iloc[i - 1]:
			obv.append(obv[-1] - data["Volume"].iloc[i])
		else:
			obv.append(obv[-1])
	return obv


"""
B. VWAP (Volume Weighted Average Price)
~ Use Case: Tracks the average price weighted by volume.

🔹 Trading Insight:
~ Price above VWAP → Bullish sentiment
~ Price below VWAP → Bearish sentiment
"""
