import pandas as pd
import os

class Scan:
    def __init__(self, indicator, stock_data):
        self.indicator = indicator
        self.stock_data = stock_data

    def scan_ta(self, condition):
        result = []

        # Check which indicator to use
        if condition["indicator"] == "sma":
            #This if else condition works when the case is sent empty in the dictionary, so that the case is the last price.
            if condition["case"] == "":
                case = self.stock_data.get_stock_data()["Last Price"]
                con_v1 = self.indicator.sma_indicator(condition["con_v1"])
                con_v2 = self.indicator.sma_indicator(condition.get("con_v2", 10))
            else:
                case = self.indicator.sma_indicator(condition["case"])
                con_v1 = self.indicator.sma_indicator(condition["con_v1"])
                con_v2 = self.indicator.sma_indicator(condition.get("con_v2", 10))

        # Handle EMA indicator
        elif condition["indicator"] == "ema":
            if condition["case"] == "":
                case = self.stock_data.get_stock_data()["Last Price"]
                con_v1 = self.indicator.ema_indicator(condition["con_v1"])
                con_v2 = self.indicator.ema_indicator(condition.get("con_v2", 10))
            else:
                case = self.indicator.ema_indicator(condition["case"])
                con_v1 = self.indicator.ema_indicator(condition["con_v1"])
                con_v2 = self.indicator.ema_indicator(condition.get("con_v2", 10))

        # Handle RSI indicator
        elif condition["indicator"] == "rsi":
            case = self.indicator.rsi_indicator()
            con_v1 = condition["con_v1"]
            con_v2 = condition.get("con_v2", 10)

        # Handle Relative Volume indicator
        elif condition["indicator"] == "rel_vol":
            case = self.indicator.relative_vol(condition.get("case", 10))
            con_v1 = condition["con_v1"]
            con_v2 = condition.get("con_v2", 1)

        # Handle ADX indicator
        elif condition["indicator"] == "adx":
            case = self.indicator.adx_indicator(condition.get("case", 14))
            con_v1 = condition["con_v1"]
            con_v2 = condition.get("con_v2", 10)

        # Handle Golden/Death Cross condition
        elif condition["indicator"] == "g_d_cross":
            case = self.indicator.golden_dead_cross()["Cross"].iloc[-1] == "Golden Cross"
            con_v1 = self.indicator.golden_dead_cross()["Cross"].iloc[-2] == "Golden Cross"
            con_v2 = 10
        # Handle MACD indicator
        elif condition["indicator"] == "macd":
            case = self.indicator.macd_indicator()["signal"].iloc[-1] == "Positive Signal"
            con_v1 = self.indicator.macd_indicator()["signal"].iloc[-2] == "Positive Signal"
            con_v2 = 10

        # Raise an error if the indicator is unsupported
        else:
            raise ValueError(f"Unsupported indicator type: {condition['indicator']}")

        # Function to extract the latest value from a Series or return the value itself
        def get_value(val):
            if isinstance(val, pd.Series):
                return val.iloc[-1]
            else:
                return val

        # Extract final values for comparison
        case_val = get_value(case)
        con_v1_val = get_value(con_v1)
        con_v2_val = get_value(con_v2)
        vals = [case_val, con_v1_val, con_v2_val]

        # If any value is None, return False
        if None in vals: #In the indicator class, it returns none when no indicator is entered in the appropriate period.
            return False

        # Apply condition checks
        if condition["condition"] == ">":
            return case_val >= con_v1_val
        elif condition["condition"] == "<":
            return case_val <= con_v1_val
        elif condition["condition"] == "cut_up":
            if isinstance(case, pd.Series) and isinstance(con_v1, pd.Series):
                return case.iloc[-1] >= con_v1.iloc[-1] and case.iloc[-2] < con_v1.iloc[-2]
            elif isinstance(case, pd.Series):
                return case.iloc[-1] >= con_v1 and case.iloc[-2] < con_v1
            else:
                return False  # Return False for non-Series values

        elif condition["condition"] == "cut_down":
            if isinstance(case, pd.Series) and isinstance(con_v1, pd.Series):
                return case.iloc[-1] <= con_v1.iloc[-1] and case.iloc[-2] > con_v1.iloc[-2]
            elif isinstance(case, pd.Series):
                return case.iloc[-1] <= con_v1 and case.iloc[-2] > con_v1
            else:
                return False

        elif condition["condition"] == "between":
            lower = min(con_v1_val, con_v2_val)
            upper = max(con_v1_val, con_v2_val)
            return lower <= case_val <= upper

        elif condition["condition"] == "s_value":
            return case

        elif condition["condition"] == "g_intersection":
            return case != con_v1 and case

        elif condition["condition"] == "b_intersection":
            return case != con_v1 and not case

        else:
            raise ValueError(f"Unsupported condition: {condition['condition']}")

        return False

    def scan_fa(self, condition):
        file_path = "fundamental_analysis_stocks.csv"

        # Check if the fundamental analysis data file exists
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            print(f"Error: Database is empty or not found ({self.stock_data.symbol})")
            return False

        # Read the CSV file
        try:
            df = pd.read_csv(file_path, index_col="Symbol")  # Use "Symbol" column as index
        except pd.errors.EmptyDataError:
            print(f"Error: Data file is empty({self.stock_data.symbol})")
            return False

        # If the stock is not found in the data, return an error
        if self.stock_data.symbol not in df.index:
            print(f"Error: No data found for {self.stock_data.symbol}.")
            return False

        stock_data = df.loc[self.stock_data.symbol]

        # Check if the requested financial ratio exists and is valid
        if condition["financial ratio"] not in stock_data or stock_data[condition["financial ratio"]] == "N/A":
            print(f"Error: {condition['financial ratio']} data is 'N/A' or not found ({self.stock_data.symbol}).")
            return False

        value = stock_data[condition["financial ratio"]]

        # Convert the value to a float, handling percentage signs if necessary
        try:
            if isinstance(value, str) and "%" in value:
                value = float(value.replace("%", ""))
            else:
                value = float(value)
        except ValueError:
            print(f"Error: Could not convert {condition['financial ratio']} ({self.stock_data.symbol}).")
            return False  # Return False if conversion fails

        # Apply financial condition checks
        if condition["condition"] == ">":
            return value > condition["con_v1"]
        elif condition["condition"] == "<":
            return value < condition["con_v1"]
        elif condition["condition"] == "between":
            return condition["con_v1"] < value < condition["con_v2"]
        else:
            print(f"Error: Unsupported condition {condition['condition']} ({self.stock_data.symbol}).")
            return False

    def scan(self, conditions):
        result = []
        ta_conditions = []
        fa_conditions = []

        # Separate technical analysis (TA) and fundamental analysis (FA) conditions
        for condition in conditions:
            if condition["type"] == "fa":
                fa_conditions.append(condition)
            else:
                ta_conditions.append(condition)

        # Process TA conditions
        for ta_condition in ta_conditions:
            ta_result = self.scan_ta(ta_condition)
            result.append(ta_result)

        # Process FA conditions
        for fa_condition in fa_conditions:
            fa_result = self.scan_fa(fa_condition)
            result.append(fa_result)

        # If any condition fails, return False
        if False in result:
            return False
        return True
