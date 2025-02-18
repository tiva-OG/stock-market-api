import yfinance as yf
from flask import Flask, jsonify,request
from datetime import datetime

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
	return "HELLO WORLD"


@app.get("/stock/<ticker>")
def get_stock_data(ticker: str):
	"""Fetch stock data"""
	stock = yf.Ticker(ticker)
	data = stock.history(period="1d")

	if data.empty:
		raise APITickerError("Invalid stock ticker or no data available")

	return {
		"ticker": ticker.upper(),
		"date": str(data.index[-1].date()),
		"open": round(data["Open"][-1], 2),
		"close": round(data["Close"][-1], 2),
		"high": round(data["High"][-1], 2),
		"low": round(data["Low"][-1], 2),
		"volume": int(data["Volume"][-1])
	}


@app.get("/stock/<ticker>/history")
def get_stock_history(ticker: str):
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
			"date": str(index.date()),
			"open": round(row["Open"], 2),
			"close": round(row["Close"], 2),
			"high": round(row["High"], 2),
			"low": round(row["Low"], 2),
			"volume": int(row["Volume"])
		}
		for index, row in data.iterrows()]

	return {"ticker": ticker.upper(), "history": history}


if __name__ == "__main__":
	app.run(debug=True)
