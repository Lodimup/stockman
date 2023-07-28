from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from pypfopt import EfficientFrontier, expected_returns, risk_models
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from rich import print
from services.read_cfg import read_cfg
from services.set100 import symbols
from services.backtests.batch_simple_backtest import batch_simple_backtest

CFG = read_cfg()
RISK_FREE_RATE = CFG["risk_free_rate"]
BLACKLISTS = CFG["blacklists"]


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

    # Calculate expected returns and sample covariance
    mu = expected_returns.mean_historical_return(df)
    S = risk_models.sample_cov(df)

    # Optimize for maximum Sharpe ratio
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe(risk_free_rate=RISK_FREE_RATE)
    cleaned_weights = ef.clean_weights()
    latest_prices = get_latest_prices(df)
    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=CFG["capital"])
    allocation, leftover = da.lp_portfolio()
    allocation = {k: v for k, v in allocation.items() if v > 0}

    # Create report
    report = {}
    for symbol, share in allocation.items():
        report[symbol] = {
            "price": latest_prices[symbol],
            "share": share,
            "value": latest_prices[symbol] * share,
            "percentage": cleaned_weights[symbol],
        }

    # Backtest
    backtest_res = batch_simple_backtest(
        prices=df,
        weights=weights,
        capital=CFG["capital"],
    )
    backtest_res.to_csv("out/backtest.csv")

    # Report allocation
    print("-" * 80)
    excluded = ",".join(BLACKLISTS)
    print(f"Excluded: {excluded}")
    print("Allocation:")
    total_cap_used = 0
    for symbol, data in report.items():
        print(f"{symbol}: {data['share']:.0f} shares @ {data['price']:.2f} ฿ = {data['value']:,.2f} ฿")
        total_cap_used += data["value"]
    print("-" * 80)
    print(f"Total capital used: {total_cap_used:,.2f}")
    print("-" * 80)
    # Report performance
    print("-" * 80)
    ef.portfolio_performance(verbose=True, risk_free_rate=RISK_FREE_RATE)
    print('Backtest result saved to "out/backtest.csv"')


if __name__ == "__main__":
    main()
