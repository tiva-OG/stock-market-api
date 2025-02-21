from .momentum import calculate_macd, calculate_rsi
from .price_trend import calculate_ema, calculate_sma
from .volume_based import calculate_obv


def technical_indicators(data, **kwargs):
	sma_period = kwargs.get("sma_period", 50)
	ema_period = kwargs.get("ema_period", 50)
	rsi_period = kwargs.get("rsi_period", 14)

	data["SMA"] = calculate_sma(data, period=sma_period)
	data["EMA"] = calculate_ema(data, period=ema_period)
	data["RSI"] = calculate_rsi(data, period=rsi_period)
	data["MACD"], data["MACD_Signal"] = calculate_macd(data)

	return data
