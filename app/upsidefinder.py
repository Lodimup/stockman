from tasks import download_data
from services.setall import symbols
from services.read_cfg import read_cfg
import pandas as pd
from rich import print, inspect
from datetime import datetime

CFG = read_cfg()
BLACKLISTS = CFG["blacklists"]
today_str = datetime.today().strftime('%Y-%m-%d')

symbols = [f"{symbol}.BK" for symbol in symbols() if symbol not in BLACKLISTS]

# Download financial data for all stocks in parallel
results = [download_data.delay(symbol) for symbol in symbols]

# Wait for the tasks to complete and get the results
data = [result.get() for result in results]
df = pd.DataFrame(data)
df['upside%'] = (df['targetMeanPrice'] - df['currentPrice']) / df['currentPrice'] * 100
df = df[df['recommendationKey'] == 'buy']
df = df.sort_values(by=['upside%'], ascending=False)
print(df)
df.to_csv(f'out/{today_str}_upside-finder.csv')
