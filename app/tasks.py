from celery import Celery
import yfinance as yf
import logging

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/1",
)


@app.task
def download_data(symbol):
    logging.info(f"Fetching {symbol}")
    ticker = yf.Ticker(symbol)
    ret = {
        "symbol": ticker.info.get("symbol"),
        "name": ticker.info.get("longName"),
        "currentPrice": ticker.info.get("currentPrice"),
        "targetHighPrice": ticker.info.get("targetHighPrice"),
        "targetLowPrice": ticker.info.get("targetLowPrice"),
        "targetMeanPrice": ticker.info.get("targetMeanPrice"),
        "targetMedianPrice": ticker.info.get("targetMedianPrice"),
        "recommendationMean": ticker.info.get("recommendationMean"),
        "recommendationKey": ticker.info.get("recommendationKey"),
        "numberOfAnalystOpinions": ticker.info.get("numberOfAnalystOpinions"),
    }
    logging.info(f"Fetched {symbol}")
    return ret
