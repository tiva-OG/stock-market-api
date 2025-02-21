"""50 Largest Companies in the USA by Market Cap"""
import datetime

import bs4 as bs
import requests
import yfinance as yf
from sqlalchemy import Integer, Date, Float, String, create_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, sessionmaker
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()


class Stock(Base):
	__tablename__ = "usa50_info"

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	ticker: Mapped[str] = mapped_column(Integer, unique=True)
	fullname: Mapped[str] = mapped_column(String)
	sector: Mapped[str] = mapped_column(String)
	industry: Mapped[str] = mapped_column(String)

	def __repr__(self):
		return f"Stock(ticker={self.ticker!r},  fullname={self.fullname!r}, sector={self.sector!r}, industry={self.industry!r})"


class StockData(Base):
	__tablename__ = "usa50_history"
	__table_args__ = (UniqueConstraint("ticker", "date"),)

	id: Mapped[int] = mapped_column(primary_key=True, index=True)
	ticker: Mapped[str] = mapped_column(String)
	date: Mapped[datetime.date] = mapped_column(Date)
	close: Mapped[float] = mapped_column(Float)
	high: Mapped[float] = mapped_column(Float)
	low: Mapped[float] = mapped_column(Float)
	open: Mapped[float] = mapped_column(Float)
	volume: Mapped[int] = mapped_column(Integer)

	def __repr__(self):
		return f"StockData(ticker={self.ticker!r},  date={self.date!r}, open={self.open!r}, close={self.close!r}, high={self.high!r}, low={self.low!r}, volume={self.volume})"


engine_usa50_info = create_engine("sqlite:///usa50_info.db")
engine_usa50_history = create_engine("sqlite:///usa50_history.db")
Session = sessionmaker()
Session.configure(binds={Stock: engine_usa50_info, StockData: engine_usa50_history})


def scrape_usa50_tickers() -> list:
	url = "https://companiesmarketcap.com/usa/largest-companies-in-the-usa-by-market-cap/"

	try:
		response = requests.get(url)
		soup = bs.BeautifulSoup(response.text, "lxml")
		stocks = [div.text for div in soup.find_all("div", {"class": "company-code"})[:50]]
		return stocks
	except Exception as e:
		print(e)
		return []


def download_stock_history(ticker: str, start_date: str = None, end_date: str = None, period: str = None) -> list:
	if period:
		stock_data = yf.download(ticker, period=period, multi_level_index=False)
	else:
		stock_data = yf.download(ticker, start=start_date, end=end_date, multi_level_index=False)

	return [
		{
			"date": row_id,
			"open": round(row["Open"], 2),
			"close": round(row["Close"], 2),
			"high": round(row["High"], 2),
			"low": round(row["Low"], 2),
			"volume": int(row["Volume"])
		}
		for row_id, row in stock_data.iterrows()]


def download_stock_info(ticker: str) -> dict:
	stock = yf.Ticker(ticker)
	stock_info = stock.info

	return {
		"fullname": stock_info["longName"],
		"sector": stock_info["sector"],
		"industry": stock_info["industry"]
	}


def query_all_stocks():
	with Session() as session:
		results = session.query(Stock).order_by(Stock.ticker).all()
		return results


def query_stock_history(ticker: str):
	with Session() as session:
		results = session.query(StockData).filter(StockData.ticker == ticker).order_by(StockData.date.desc()).all()
	return results


# def query_


def main() -> None:
	usa50_tickers = scrape_usa50_tickers()
	with Session() as session:
		for ticker in usa50_tickers:
			print(f"processing {ticker}")

			stock_info = download_stock_info(ticker)
			stock = Stock(ticker=ticker, fullname=stock_info.get("fullname"), sector=stock_info.get("sector"), industry=stock_info.get("industry"))
			session.add(stock)

			stock_data = download_stock_history(ticker, period="5y")
			for data in stock_data:
				_data = StockData(ticker=ticker, date=data.get("date"), open=data.get("open"), close=data.get("close"), high=data.get("high"), low=data.get("low"), volume=data.get("volume"))
				session.add(_data)
			print(_data)
		session.commit()

	print("Filling database complete!")


if __name__ == "__main__":
	Base.metadata.tables["usa50_info"].create(bind=engine_usa50_info)
	Base.metadata.tables["usa50_history"].create(bind=engine_usa50_history)
	main()
