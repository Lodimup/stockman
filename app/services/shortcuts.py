import yfinance as yf


def get_info(symbol: str) -> dict:
    """
    get info from yfinance
    Useful data:
    - trailingPE
    - recommendationKey
    - returnOnEquity  * may not be there
    - returnOnAssets  * may not be there
    """

    return yf.Ticker(symbol)

# from rich import print
# print(yf.Ticker("PTT.BK").info)
