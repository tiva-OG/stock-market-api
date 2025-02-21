from datetime import datetime

import pandas as pd
import yfinance as yf
from flask import Flask, jsonify, request, render_template

from analysis.stock import technical_indicators
from analysis.stock import momentum, price_trend
from usa50 import query_all_stocks, query_stock_history

app = Flask(__name__)


class APIError(Exception):
	"""All custom API Exceptions"""
	pass


class APITickerError(APIError):
	"""Custom Ticker Error Class"""
	code = 404
	description = "Invalid stock ticker or no data available"


@app.errorhandler(APIError)
def handle_exception(err):
	"""Return custom JSON when APIError or its children are raised """
	response = {"error": err.description, "message": "Invalid stock ticker or no data available"}
	return jsonify(response), err.code


@app.errorhandler(500)
def handle_exception(err):
	"""Return JSON for any other server error"""
	response = {"error": "Sorry, that error is on us, please contact support if this wasn't an accident", "message": ""}
	return jsonify(response), 500


@app.route("/")
def index():
	stocks = query_all_stocks()
	return render_template("index.html", stocks=stocks)


@app.route("/stock/<ticker>")
def get_stock_data(ticker: str):
	"""Fetch stock data"""
	stock = yf.Ticker(ticker)
	data = stock.history(period="2d")

	if data.empty:
		raise APITickerError("Invalid stock ticker or no data available")

	latest = data.iloc[-1]
	previous = data.iloc[-2] if len(data) > 1 else latest  # handle cases where only data for a single day is available
	change = round(((latest["Close"] - previous["Close"]) / previous["Close"]) * 100, 2)

	return {
		"ticker": ticker.upper(),
		"date": str(latest.name.date()),
		"open": round(latest["Open"], 2),
		"close": round(latest["Close"], 2),
		"high": round(latest["High"], 2),
		"low": round(latest["Low"], 2),
		"volume": int(latest["Volume"]),
		"change_percentage": f"{change}%"
	}


@app.route("/stock/<ticker>/history")
def check_stock_history(ticker: str):
	stock_history = query_stock_history(ticker)
	return render_template("stock_history.html", ticker=ticker, stock_history=stock_history)


@app.route("/stock/ticker2")
def get_stock_history2(ticker: str):
	"""Fetch historical stock data between start and end dates"""
	start = request.args.get("start")
	end = request.args.get("end")

	stock = yf.Ticker(ticker)
	start_date = datetime.strptime(start, "%Y-%m-%d").date()
	end_date = datetime.strptime(end, "%Y-%m-%d").date()
	data = stock.history(start=str(start_date), end=str(end_date))

	if data.empty:
		raise APITickerError("No data available for the given data range.")

	history = [
		{
			"date": str(row_id.date()),
			"open": round(row["Open"], 2),
			"close": round(row["Close"], 2),
			"high": round(row["High"], 2),
			"low": round(row["Low"], 2),
			"volume": int(row["Volume"])
		}
		for row_id, row in data.iterrows()]

	return {"ticker": ticker.upper(), "history": history}


@app.route("/stock/<ticker>/technical-indicators", methods=["GET"])
def get_technical_indicators(ticker:str):
	sma_period = int(request.args.get("sma_period", 50))
	ema_period = int(request.args.get("ema_period", 50))
	rsi_period = int(request.args.get("rsi_period", 50))

	stock_history = query_stock_history(ticker)
	stock_df = pd.DataFrame([(data.date, data.open, data.close, data.high, data.low, data.volume) for data in stock_history], columns=["Date", "Open", "Close", "High", "Low", "Volume"])
	stock_df = technical_indicators(stock_df, sma_period=sma_period, ema_period=ema_period, rsi_period=rsi_period)

	return jsonify(stock_df.to_dict(orient="records"))


@app.route("/stock/<ticker>/sma", methods=["GET"])
def get_stock_sma(ticker: str):
	period = int(request.args.get("period", 20))
	stock_history = query_stock_history(ticker)
	stock_df = pd.DataFrame([(data.date, data.open, data.close, data.high, data.low, data.volume) for data in stock_history], columns=["Date", "Open", "Close", "High", "Low", "Volume"])
	stock_df["SMA"] = price_trend.calculate_sma(stock_df, period=period)
	return jsonify(stock_df[["Date", "SMA"]].dropna().to_dict(orient="records"))


@app.route("/stock/<ticker>/ema", methods=["GET"])
def get_stock_ema(ticker: str):
	period = int(request.args.get("period", 20))
	stock_history = query_stock_history(ticker)
	stock_df = pd.DataFrame([(data.date, data.open, data.close, data.high, data.low, data.volume) for data in stock_history], columns=["Date", "Open", "Close", "High", "Low", "Volume"])
	stock_df["EMA"] = price_trend.calculate_ema(stock_df, period=period)
	return jsonify(stock_df[["Date", "EMA"]].dropna().to_dict(orient="records"))


@app.route("/stock/<ticker>/rsi", methods=["GET"])
def get_stock_rsi(ticker: str):
	period = int(request.args.get("period", 14))
	stock_history = query_stock_history(ticker)
	stock_df = pd.DataFrame([(data.date, data.open, data.close, data.high, data.low, data.volume) for data in stock_history], columns=["Date", "Open", "Close", "High", "Low", "Volume"])
	stock_df["RSI"] = momentum.calculate_rsi(stock_df, period=period)
	return jsonify(stock_df[["Date", "RSI"]].dropna().to_dict(orient="records"))


@app.route("/stock/<ticker>/macd", methods=["GET"])
def get_stock_macd(ticker: str):
	stock_history = query_stock_history(ticker)
	stock_df = pd.DataFrame([(data.date, data.open, data.close, data.high, data.low, data.volume) for data in stock_history], columns=["Date", "Open", "Close", "High", "Low", "Volume"])
	stock_df["MACD"], stock_df["MACD_Signal"] = momentum.calculate_macd(stock_df)
	return jsonify(stock_df[["Date", "MACD", "MACD_Signal"]].dropna().to_dict(orient="records"))


if __name__ == "__main__":
	app.run(debug=True)
