import json


def read_data() -> dict:
    """
    goto https://www.settrade.com/th/equities/market-data/overview?category=Index&market=set&index=SET100
    look for json resp from https://www.settrade.com/api/set/index/SET100/composition
    """
    with open('data/set100.json', 'r') as f:
        data = json.load(f)
    return data


def symbols() -> list[str]:
    data = read_data()
    symbols = []
    for stock in data['composition']['stockInfos']:
        symbols.append(stock['symbol'])
    return symbols
