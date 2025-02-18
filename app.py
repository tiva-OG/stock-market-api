import yfinance as yf
from flask import Flask, jsonify

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


if __name__ == "__main__":
	app.run(debug=True)
