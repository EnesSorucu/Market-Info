import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pdb

class StockChart:
    def __init__(self, symbol, indicator):
        self.symbol = symbol
        self.directory = f"./datafolder/{symbol}.csv"
        self.indicator = indicator

    def load_data(self):
        try:
            df = pd.read_csv(self.directory)
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
            df = df.dropna(subset=['Date'])
            df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
            df["Open"] = pd.to_numeric(df["Open"], errors='coerce')
            df["High"] = pd.to_numeric(df["High"], errors='coerce')
            df["Low"] = pd.to_numeric(df["Low"], errors='coerce')
            df["Volume"] = pd.to_numeric(df["Volume"], errors='coerce')
            return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return pd.DataFrame()

    def stock_chart(self, period=0, indicators={}):
        df = self.load_data()
        if df.empty:
            print("Failed to load data.")
            return

        today = pd.to_datetime("today").date()
        if period > 0:
            start_date = today - pd.Timedelta(days=period)
            df = df[df["Date"] >= start_date]

        df = df[df["Volume"] > 0]

        valid_dates = df["Date"].tolist()

        rows = 2
        if "RSI" in indicators: rows += 1
        if "ADX" in indicators: rows += 1
        if "MACD" in indicators: rows += 1

        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            row_heights=[0.7, 0.2] + [0.15] * (rows - 2),
            vertical_spacing=0.02
        )
        #candlestick chart
        candlestick = go.Candlestick(
            x=[str(date) for date in valid_dates],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Fiyat"
        )
        fig.add_trace(candlestick, row=1, col=1)

        # SMA
        if "SMA" in indicators:
            sma_periods = indicators["SMA"]
            if not isinstance(sma_periods, list):
                sma_periods = [sma_periods]

            for sma_period in sma_periods:
                df[f"SMA{sma_period}"] = self.indicator.sma_indicator(sma_period)
                sma_data = df.dropna(subset=[f"SMA{sma_period}"])

                sma_line = go.Scatter(
                    x=[str(date) for date in sma_data["Date"]],
                    y=sma_data[f"SMA{sma_period}"],
                    mode="lines",
                    name=f"SMA {sma_period}",
                    line=dict(color="blue")
                )
                fig.add_trace(sma_line, row=1, col=1)
                fig.update_layout(
                    xaxis2_rangeslider_visible=False,
                    xaxis2_type="category"
                )

        # EMA
        if "EMA" in indicators:
            ema_periods = indicators["EMA"]
            if not isinstance(ema_periods, list):
                ema_periods = [ema_periods]

            for ema_period in ema_periods:
                df[f"EMA{ema_period}"] = self.indicator.ema_indicator(ema_period)
                ema_data = df.dropna(subset=[f"EMA{ema_period}"])

                ema_line = go.Scatter(
                    x=[str(date) for date in ema_data["Date"]],
                    y=ema_data[f"EMA{ema_period}"],
                    mode="lines",
                    name=f"EMA {ema_period}",
                    line=dict(color="orange")
                )
                fig.add_trace(ema_line, row=1, col=1)

        # Bollinger Bands
        if "Bollinger" in indicators and indicators["Bollinger"]:
            bollinger = self.indicator.bollinger_bands()
            df["mid_band"] = bollinger["mid_band"]
            df["upper_band"] = bollinger["upper_band"]
            df["lower_band"] = bollinger["lower_band"]

            boll_data = df.dropna(subset=["mid_band", "upper_band", "lower_band"])

            mid_band = go.Scatter(
                x=[str(date) for date in boll_data["Date"]],
                y=boll_data["mid_band"],
                mode="lines",
                name="Bollinger Mid",
                line=dict(color="purple", dash="dot")
            )

            upper_band = go.Scatter(
                x=[str(date) for date in boll_data["Date"]],
                y=boll_data["upper_band"],
                mode="lines",
                name="Bollinger Üst",
                line=dict(color="red", dash="dash")
            )

            lower_band = go.Scatter(
                x=[str(date) for date in boll_data["Date"]],
                y=boll_data["lower_band"],
                mode="lines",
                name="Bollinger Alt",
                line=dict(color="green", dash="dash")
            )

            fig.add_traces([mid_band, upper_band, lower_band], rows=[1, 1, 1], cols=[1, 1, 1])

        volume_data = df.dropna(subset=["Volume"])

        volume_colors = ["green" if close >= open_ else "red" for close, open_ in zip(df["Close"], df["Open"])]

        volume_bars = go.Bar(
            x=df["Date"].astype(str),
            y=df["Volume"],
            name="Hacim",
            marker=dict(color=volume_colors),
            showlegend=False
        )

        fig.add_trace(volume_bars, row=2, col=1)
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            xaxis_type="category",

            xaxis2=dict(
                rangeslider_visible=False,
                type="category"
            ),

            yaxis2=dict(
                title="Hacim",
                side="left",
                showgrid=False,
                anchor="x2"
            )
        )
        df["relative_vol"] = self.indicator.relative_vol()

        relative_vol_plot = go.Scatter(
            x=df["Date"].astype(str),
            y=df["relative_vol"],
            mode="lines",
            name="Bağıl Hacim",
            line=dict(color="blue"),
            yaxis="y2"
        )

        fig.add_trace(relative_vol_plot, row=2, col=1)
        fig.update_layout(
            xaxis2_rangeslider_visible=False,
            xaxis2_type="category",
            yaxis2=dict(
                overlaying="y2",
                side="left",
                showgrid=False,
                title="Bağıl Hacim"
            )
        )

        row_idx = 3
        if "RSI" in indicators:
            rsi_period = indicators["RSI"]
            df["RSI"] = self.indicator.rsi_indicator(rsi_period)
            rsi_data = df.dropna(subset=["RSI"])

            rsi_plot = go.Scatter(
                x=[str(date) for date in rsi_data["Date"]],
                y=rsi_data["RSI"],
                mode="lines",
                name=f"RSI {rsi_period}",
                line=dict(color="purple")
            )

            fig.add_trace(rsi_plot, row=row_idx, col=1)
            fig.update_yaxes(range=[0, 100], row=row_idx, col=1)
            row_idx += 1
            fig.update_layout(
                xaxis2_rangeslider_visible=False,
                xaxis2_type="category"
            )

        if "ADX" in indicators:
            adx_period = indicators["ADX"]
            df["ADX"] = self.indicator.adx_indicator(adx_period)
            adx_data = df.dropna(subset=["ADX"])

            adx_plot = go.Scatter(
                x=[str(date) for date in adx_data["Date"]],
                y=adx_data["ADX"],
                mode="lines",
                name=f"ADX {adx_period}",
                line=dict(color="red")
            )

            fig.add_trace(adx_plot, row=row_idx, col=1)
            fig.update_layout(
                xaxis2_rangeslider_visible=False,
                xaxis2_type="category"
            )
            row_idx += 1

        if "MACD" in indicators:
            macd = self.indicator.macd_indicator()
            df["MACD"] = macd["macd"]
            macd_data = df.dropna(subset=["MACD"])

            macd_plot = go.Scatter(
                x=[str(date) for date in macd_data["Date"]],
                y=macd_data["MACD"],
                mode="lines",
                name="MACD"
            )

            fig.add_trace(macd_plot, row=row_idx, col=1)
            fig.update_layout(
                xaxis2_rangeslider_visible=False,
                xaxis2_type="category"  #
            )

        fig.update_layout(
            title=f"{period} Günlük {self.symbol} Grafik",
            xaxis_rangeslider_visible=False,
            xaxis_type="category"
        )

        fig.show()
