import pandas as pd
from pypfopt.discrete_allocation import DiscreteAllocation
from services.console import console
from services.read_cfg import read_cfg

CFG = read_cfg()


def simple_backtest(
        buy_date: str,
        sell_date: str,
        prices: pd.DataFrame,
        weights: dict[str, float],
        capital: float,
) -> float:
    """Calculate gain(loss) from backtest

    Args:
        buy_date (str): buy date in YYYY-MM-DD format
        sell_date (str): sell date in YYYY-MM-DD format
        prices (pd.DataFrame): prices dataframe
        weights (dict[str, float]): weights dict
        capital (float, optional): capital. Defaults to CFG["capital"].

    Returns:
        float: gain(loss)
    """
    weights = {k: v for k, v in weights.items() if v > 0}
    prices = prices[[k for k in weights.keys()]]
    buy_prices = prices.loc[buy_date]
    sell_prices = prices.loc[sell_date]
    da = DiscreteAllocation(weights, buy_prices, total_portfolio_value=capital)
    allocation, leftover = da.lp_portfolio()

    total_gain = 0
    for k, v in allocation.items():
        sell_price = sell_prices[k]
        buy_price = buy_prices[k]
        gain = (sell_price - buy_price) * v
        total_gain += gain
        if sell_price/buy_price > CFG['unusual_gain_warn']:
            console.print(f"\n{k} {buy_date} {sell_date} {buy_price:.2f} {sell_price:.2f}", style="red")

    return total_gain
