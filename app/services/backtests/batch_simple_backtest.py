import pandas as pd
from datetime import timedelta
from services.backtests.simple_backtest import simple_backtest
from services.helpers import dt2str
import pypfopt
from rich.progress import track


def batch_simple_backtest(
        prices: pd.DataFrame,
        weights: dict[str, float],
        capital: float,
) -> pd.DataFrame:
    """
    Batch calculate gain(loss) from backtest
    TODO: handle KeyError by shifting date or find next date closest to timedelta

    Args:
        prices (pd.DataFrame): prices dataframe
        weights (dict[str, float]): weights dict
        capital (float, optional): capital. Defaults to CFG["capital"].
    Returns:
        list[dict[str, float]]: list of gain(loss) dict
    """
    gains = {
        "buy_date": [],
        "sell_date": [],
        "gain": [],
    }
    for date in track(prices.index, description="Backtesting..."):
        buy_date = date
        sell_date = date + timedelta(days=365)
        try:
            prices.loc[sell_date]
        except KeyError:
            continue
        try:
            gain = simple_backtest(
                buy_date=dt2str(buy_date),
                sell_date=dt2str(sell_date),
                prices=prices,
                weights=weights,
                capital=capital,
            )
            gains["buy_date"].append(buy_date)
            gains["sell_date"].append(sell_date)
            gains["gain"].append(gain)
        except pypfopt.exceptions.OptimizationError:
            continue

    return pd.DataFrame(gains).set_index("buy_date")
