import json


def read_data(path) -> dict:
    """
    goto https://www.settrade.com/th/equities/market-data/overview?category=Index&market=set&index=SET100
    look for json resp from https://www.settrade.com/api/set/index/SET100/composition
    """
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def extract_symbols(data: dict) -> list[str]:
    symbols = []
    for sub_indice in data['composition']['subIndices']:
        for stock in sub_indice['stockInfos']:
            symbols.append(stock['symbol'])
    return symbols


def symbols() -> list[str]:
    agro = read_data('data/agro.json')
    consump = read_data('data/consump.json')
    fincial = read_data('data/fincial.json')
    indus = read_data('data/indus.json')
    propcon = read_data('data/propcon.json')
    resourc = read_data('data/resourc.json')
    service = read_data('data/service.json')
    tech = read_data('data/tech.json')

    agro = extract_symbols(agro)
    consump = extract_symbols(consump)
    fincial = extract_symbols(fincial)
    indus = extract_symbols(indus)
    propcon = extract_symbols(propcon)
    resourc = extract_symbols(resourc)
    service = extract_symbols(service)
    tech = extract_symbols(tech)

    return agro + consump + fincial + indus + propcon + resourc + service + tech