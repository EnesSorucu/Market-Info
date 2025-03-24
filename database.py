import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
from tabulate import tabulate
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class StockData:
    def __init__(self, symbol):
        self.symbol = symbol
        self.folder = "./datafolder"
        self.file_csv = f"{self.symbol}.csv"
        self.directory = f"{self.folder}/{self.file_csv}"

    def historical_price_data(self, days=1200):
        today = datetime.now()

        os.makedirs(self.folder, exist_ok=True)
        if self.file_csv in os.listdir(self.folder):
            df = pd.read_csv(self.directory)
            df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
            past = df["Date"].max()
            if past > today:
                print("⚠️ No new data: Deadline is after today.")
                return

            last_d = yf.download(self.symbol, period="1d")
            last_d = last_d.reset_index()
            if last_d.empty:
                print("Last day data could not be obtained.")
                return

            last_v_in_csv = int(df["Volume"].iloc[-1])
            last_v = int(last_d["Volume"].stack().iloc[-1])
            if last_v == last_v_in_csv:
                print(f"{self.symbol} data is up to date")
                return
            else:
                df = df.iloc[:-1]

                new_df = yf.download(self.symbol, start=past, end=today)

                new_df.columns = new_df.columns.droplevel(1) if isinstance(new_df.columns, pd.MultiIndex) else new_df.columns

                new_df = new_df.reset_index()[['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]
                new_df['Date'] = new_df['Date'].dt.strftime('%Y-%m-%d')

                df_combined = pd.concat([df, new_df], ignore_index=True)

                df_combined.to_csv(self.directory, index=False)

                print(f"New data was added to existing {self.symbol} data and written to CSV successfully.")
        else:
            today = datetime.now() + timedelta(days=1)
            today = today.strftime("%Y-%m-%d")

            data = yf.download(self.symbol, start="2000-01-03", end=today)
            data = data.reset_index()

            df = pd.DataFrame(data)[['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]

            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

            df.to_csv(self.directory, index=False)

            print(f"✅New CSV created: {self.directory}")

    def get_stock_data(self, do_print="n"):
        stock = yf.Ticker(self.symbol)
        info = stock.info

        stock_name = info.get("longName", self.symbol)
        last_price = info.get("regularMarketPrice", info.get("currentPrice"))

        if info.get("sharesOutstanding") and info.get("floatShares"):
            circulation_rate = (info.get("floatShares") / info.get("sharesOutstanding")) * 100
        else:
            circulation_rate = "N/A"

        new_data = {
            "Symbol": self.symbol,
            "Stock Name": stock_name,
            "Last Price": last_price if last_price is not None else "N/A",
            "PE": info.get("trailingPE") if info.get("trailingPE") is not None else "N/A",
            "PB": info.get("priceToBook") if info.get("priceToBook") is not None else "N/A",
            "ROE": info.get("returnOnEquity") if info.get("returnOnEquity") is not None else "N/A",
            "EV/EBITDA": info.get("enterpriseToEbitda") if info.get("enterpriseToEbitda") is not None else "N/A",
            "Debt/Equity": (
                round(info.get("totalDebt", 0) / info.get("totalStockholdersEquity"), 2)
                if info.get("totalStockholdersEquity") else "N/A"
            ),
            "Total Shares": info.get("sharesOutstanding", "N/A"),
            "Public Shares": info.get("floatShares", "N/A"),
            "Circulation Rate": f"{round(circulation_rate, 2)}%" if circulation_rate != "N/A" else "N/A",
            "Market Cap": info.get("marketCap", "N/A"),
        }

        file_path = "fundamental_analysis_stocks.csv"

        # If CSV file does not exist, create it with column names
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            columns = ["Symbol", "Stock Name", "Last Price", "PE", "PB", "ROE",
                       "EV/EBITDA", "Debt/Equity", "Total Shares", "Public Shares",
                       "Circulation Rate", "Market Cap"]
            df_old = pd.DataFrame(columns=columns)
        else:
            try:
                df_old = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                df_old = pd.DataFrame(columns=["Symbol", "Stock Name", "Last Price", "PE", "PB", "ROE",
                                               "EV/EBITDA", "Debt/Equity", "Total Shares", "Public Shares",
                                               "Circulation Rate", "Market Cap"])

        if self.symbol in df_old["Symbol"].values:
            last_saved_price = df_old[df_old["Symbol"] == self.symbol]["Last Price"].values[0]

            if last_price == last_saved_price:
                print(f"{self.symbol} için fiyat değişmedi, veri güncellenmedi.")
                return df_old

            print(f"Data updated: {self.symbol}")

        df_old = df_old[df_old["Symbol"] != self.symbol]

        df_new = pd.DataFrame([new_data])
        df_updated = pd.concat([df_old, df_new], ignore_index=True)

        df_updated.fillna("N/A", inplace=True)
        df_updated.to_csv(file_path, index=False)

        print(f"Added new stock: {self.symbol} ({stock_name})")

        if do_print == "y":
            print(tabulate(new_data.items(), headers=["Metric", "Value"], tablefmt="fancy_grid"))

        return df_updated

