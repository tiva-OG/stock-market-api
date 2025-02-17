from flask import Flask
import yfinance as yf

app = Flask(__name__)


@app.route("/")
def index():
	return "HELLO WORLD"


@app.get("/stock/<string:ticker>")
def get_stock_data(ticker):
	stock = yf.Ticker(ticker)
	data = stock.history(period="1d")

	if data.empty:
		return {"error": "Invalid stock ticker or no data available"}

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
