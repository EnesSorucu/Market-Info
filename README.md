# Market-Info

This project is a Python application that downloads and updates historical price data and fundamental analysis data for stocks using the **yfinance** library. It calculates technical indicators and generates interactive stock charts using Plotly, providing users with comprehensive stock market insights.


## Features

- **Download and update historical price data** for stocks.  
- **Retrieve and update fundamental analysis data**, including PE, PB, ROE, EV/EBITDA, Debt/Equity, and more.  
- **Calculate technical indicators**: SMA, EMA, RSI, ADX, Relative Volume, MACD, Bollinger Bands, Golden/Death Cross.  
- **Generate interactive stock charts** with Plotly, including candlestick charts, volume, and technical indicators.  
- **Store data** in CSV format in the `datafolder_directory`.  
- Fundamental analysis data is stored in `fundamental_analysis_stocks.csv`.  

## Requirements

Python 3.x and the following libraries:

- `yfinance`  
- `pandas`  
- `pandas_ta`  
- `numpy`  
- `plotly`  
- `tabulate`  
- `warnings`

### Install Required Libraries

```bash
pip install yfinance pandas pandas_ta numpy plotly tabulate

## Usage

### Download Data for Multiple Stocks

Downloads both price and fundamental data for the specified list of stocks.

**Note**: For BIST stocks, do not add ".IS" at the end of the symbol.  
For BIST stock symbols, you can look up `STOCK_N.py`.

```python
stock_list = ["AAPL", "THYAO.IS", "EREGL.IS", "TSLA"]
download_all_stock_d(stock_list)

from stock_data import StockData

stock = StockData("AAPL")
stock.historical_price_data()  # Download historical price data to `datafolder`
stock.get_stock_data()       # Retrieve fundamental analysis data to `fundamental_analysis_stocks.csv`

## Calculate Technical Indicators

```python
from indicators import Indicator

indicator = Indicator("AAPL")

sma = indicator.sma_indicator(period=50)        # Simple Moving Average (SMA)
ema = indicator.ema_indicator(period=50)        # Exponential Moving Average (EMA)
rsi = indicator.rsi_indicator(period=14)        # Relative Strength Index (RSI)
adx = indicator.adx_indicator(period=14)        # Average Directional Index (ADX)
relative_vol = indicator.relative_vol(period=10)  # Relative Volume
macd = indicator.macd_indicator()              # MACD
bollinger = indicator.bollinger_bands()        # Bollinger Bands
cross_signals = indicator.golden_dead_cross()  # Golden/Death Cross
```
### Generate Stock Charts
```python
from stock_chart import StockChart
from indicators import Indicator

indicator = Indicator("AAPL")
chart = StockChart("AAPL", indicator)

indicators = {
    "SMA": [20, 50],
    "EMA": 20,
    "RSI": 14,
    "ADX": 14,
    "MACD": True,
    "Bollinger": True
}
```
chart.stock_chart(period=180, indicators=indicators)```

## Data Format

### Price Data Format (`datafolder/{symbol}.csv`)

| Date       | Close  | High   | Low    | Open   | Volume   |
|------------|--------|--------|--------|--------|----------|
| 2025-03-24 | 150.25 | 152.00 | 148.50 | 149.00 | 5000000  |

---

### Fundamental Analysis Data Format (`fundamental_analysis_stocks.csv`)

| Symbol   | Stock Name                          | Last Price | PE       | PB       | ROE     | EV/EBITDA | Debt/Equity | Total Shares  | Public Shares | Circulation Rate | Market Cap      |
|----------|-------------------------------------|------------|----------|----------|---------|-----------|-------------|---------------|----------------|-------------------|------------------|
| THYAO.IS | Türk Hava Yollari Anonim Ortakligi   | 285.75     | 3.478393 | 0.579977 | 0.19937 | 6.376     | N/A         | 1375149952.0  | 702060610.0    | 51.05%            | 392949104640.0   |

## Technical Indicators Output

- **SMA/EMA**: Moving average values.  
- **RSI**: Momentum indicator for overbought/oversold conditions.  
- **ADX**: Trend strength indicator.  
- **Relative Volume**: Current volume relative to average volume.  
- **MACD**: Line, signal line, histogram interpretation.  
- **Bollinger Bands**: Mid, upper, and lower bands.  
- **Golden/Death Cross**: SMA 50 and SMA 200 cross points.  

---

## Notes

- If you want to get up-to-date data every time you use it, update the data 
- Yahoo Finance data may contain inaccuracies.  
- Sample usage is available in `main.py`.
- Indicators do not contain investment advice

## Common Error Fix

If you encounter this error:

```pgsql
ImportError: cannot import name 'NaN' from 'numpy'
Fix it by changing:
```

``` python
from numpy import NaN as npNaN
```
to:

``` python
from numpy import nan as npNaN
```
