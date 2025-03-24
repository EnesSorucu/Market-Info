import time
from database import StockData
from Indicator import Indicator
from scan import Scan
from STOCK_N import stock as stock_list
from chart import StockChart

def download_all_stock_d(stock_n_l):
    for stock in stock_n_l:
        stock_object_data = StockData(stock)  #
        stock_object_data.historical_price_data()
        stock_object_data.get_stock_data()
        time.sleep(0.2)

def scan_all(condition_list, symbol_list):
    match_l = []
    scan_objts = []

    for symbol in symbol_list:
        indicator_obj = Indicator(symbol)
        data_obj = StockData(symbol)
        scan_obj = Scan(indicator_obj, data_obj)
        scan_objts.append(scan_obj)

    for scan_obj in scan_objts:
        result = scan_obj.scan(condition_list)
        if result:
            match_l.append(scan_obj.indicator.stock_c)

    return match_l

#download_all_stock_d(stock_list)
d = StockData("A1CAP.IS")
d.historical_price_data()
d.get_stock_data()
indicator = Indicator("A1CAP.IS")
chart = StockChart("A1CAP.IS", indicator)


# Create chart object and display chart

chart.stock_chart(period=150, indicators ={
    "RSI": 14,                                 #grafikte istenen indikatörleri koymak için örnek
    "EMA": [10,25],
    "MACD": True
})

#Some condition examples for scan technical analysis

#condition1 = {"type": "ta" ,"indicator": "ema" ,"case": 50, "condition": "cut_down", "con_v1": 200}
#condition2 = {"type": "ta" ,"indicator": "rsi" ,"condition": "cut_down","con_v1": 50}
#condition3 = {"type": "ta" ,"indicator": "rel_vol", "condition": ">", "con_v1": 2}
#condition4 = {"type": "ta" ,"indicator": "sma" ,"case": "","condition": "between", "con_v1": 10, "conv2":25}
#condition5 = {"type": "ta" ,"indicator": "adx" ,"condition": "between","con_v1": 15, "con_v2": 25}
#condition6 = {"type": "ta" ,"indicator": "macd" ,"condition":"g_intersection"}
#scan temel analiz için bazı koşul örnekleri
#conditionfa1 = {"type": "fa" ,"financial ratio": "PE" ,"condition": "<", "con_v1": 10}
conditions_l = []
stock_l = stock_list
#tarama çağırma örneği
a = scan_all(condition_list=conditions_l, symbol_list=stock_l)

#my indicator
#condition_ = {"type": "ta" ,"indicator": "ema" ,"case": 5, "condition": "cut_up", "con_v1": 20} #controls the short-term trend
#condition__ = {"type": "ta" ,"indicator": "rsi" ,"condition": "cut_up","con_v1": 50} #controls momentum
#condition___ = {"type": "ta" ,"indicator": "rel_vol", "condition": ">", "con_v1": 2} #checks the market is here
