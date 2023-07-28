import time
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from pypfopt import EfficientFrontier, expected_returns, risk_models
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from rich import print
from rich.table import Table
from services.backtests.batch_simple_backtest import batch_simple_backtest
from services.console import console
from services.read_cfg import read_cfg
from services.set100 import symbols

CFG = read_cfg()
RISK_FREE_RATE = CFG["risk_free_rate"]
BLACKLISTS = CFG["blacklists"]
OUT_PREFIX = int(time.time())
SETTRADE_QUOTE_URL = 'https://www.settrade.com/th/equities/quote'


def main():
    # Create list of symbols
    tickers: list[str] = [
        f"{symbol}.BK" for symbol in symbols() if symbol not in BLACKLISTS
    ]

    # Download historical data for the assets in the portfolio
    df: pd.DataFrame = yf.download(
        tickers,
        start=datetime.now() - timedelta(days=365 * 5),
        end=datetime.now(),
    )
    df = df.fillna(method="bfill")
    df = df["Adj Close"]
    df.to_csv(f"out/{OUT_PREFIX}-prices.csv")

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    # Optimize for maximum Sharpe ratio
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe(risk_free_rate=RISK_FREE_RATE)
    cleaned_weights = ef.clean_weights()
    latest_prices = get_latest_prices(df)
    da = DiscreteAllocation(
        weights, latest_prices, total_portfolio_value=CFG["capital"]
    )
    allocation, leftover = da.lp_portfolio()
    allocation = {k: v for k, v in allocation.items() if v > 0}

    # Create report
    report = {}
    for symbol, share in allocation.items():
        report[symbol] = {
            "price": latest_prices[symbol],
            "share": share,
            "value": latest_prices[symbol] * share,
            "percentage": cleaned_weights[symbol]
        }

    # Backtest
    if CFG["backtest"]:
        backtest_res = batch_simple_backtest(
            prices=df,
            weights=weights,
            capital=CFG["capital"],
        )
        backtest_save_path = f"out/{OUT_PREFIX}-backtest.csv"
        backtest_res.to_csv(backtest_save_path)
        pd.DataFrame(report).T.to_csv(f"out/{OUT_PREFIX}-allocation.csv")
        print(f'Backtest result saved to "{backtest_save_path}')
    # Report allocation
    table = Table(title="Allocation")
    cols = [
        "Symbol",
        "Share",
        "Price",
        "Value",
        "Percentage",
        "recommendationKey",
        "trailingPE",
        "targetMeanPrice",
        "upside%",
        "Source",
    ]
    for col in cols:
        table.add_column(col)
    print("-" * 80)
    excluded = ",".join(BLACKLISTS)
    print(f"Excluded: {excluded}")
    total_cap_used = 0
    for symbol, data in report.items():
        if data["share"] <= 1:
            continue
        ticker = yf.Ticker(symbol)
        recommendation_key = ticker.info.get("recommendationKey")
        trailing_pe = ticker.info.get("trailingPE") if ticker.info.get("trailingPE") else 0
        target_mean_price = ticker.info.get("targetMeanPrice")
        upside = (target_mean_price - data["price"]) / data["price"] * 100
        symbol = symbol.split(".")[0]
        stock_url = f"{SETTRADE_QUOTE_URL}/{symbol}/overview"
        table.add_row(
            symbol,
            f"{data['share']:.0f}",
            f"{data['price']:.2f}",
            f"{data['value']:,.2f}",
            f"{data['percentage']:.2f}",
            recommendation_key,
            f"{trailing_pe:.2f}",
            f"{target_mean_price:.2f}",
            f"{upside:.2f}",
            f"[link={stock_url}][green]SETTRADE[/green][/link]",
        )
        total_cap_used += data["value"]
    console.print(table)
    print("-" * 80)
    print(f"Total capital used: {total_cap_used:,.2f}")
    # Report performance
    print("-" * 80)
    ef.portfolio_performance(verbose=True, risk_free_rate=RISK_FREE_RATE)


if __name__ == "__main__":
    main()
