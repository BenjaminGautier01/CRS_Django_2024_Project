import pandas as pd
import yfinance as yf
import talib
import plotly.graph_objects as go
import mplfinance as mpf
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource

'''
def fetch_historical_data(symbol, period, interval):
    df = yf.download(symbol, period=period, interval=interval)
    df.rename(columns={'Open': 'open', 'High': 'high', 'Low': 'low',
                       'Close': 'close', 'Adj Close': 'adj close', 'Volume': 'volume'}, inplace=True)
    return df

def clean_data(df):
    df.index = pd.to_datetime(df.index)
    return df

def identify_candlestick_patterns(df):
    pattern_functions = {name: func for name, func in talib.__dict__.items() if 'CDL' in name}
    pattern_data = []
    for name, func in pattern_functions.items():
        result = func(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
        result_df = pd.DataFrame(result, index=df.index, columns=[name])
        pattern_data.append(result_df)
    patterns = pd.concat(pattern_data, axis=1)
    return patterns

def plot_candlestick_chart(df, patterns, specific_pattern=None):
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['open'], high=df['high'],
                                         low=df['low'], close=df['close'],
                                         name="Candlesticks")])
    if specific_pattern:
        pattern_indices = patterns[patterns[specific_pattern] != 0].index
        fig.add_trace(go.Scatter(x=pattern_indices, y=df.loc[pattern_indices]['close'],
                                 mode='markers', marker=dict(color='RoyalBlue', size=8),
                                 name=specific_pattern))
    fig.update_layout(title=f'Candlestick chart with {specific_pattern} markers',
                      xaxis_title='Date', yaxis_title='Price', xaxis_rangeslider_visible=False)
    fig.show()


import mplfinance as mpf


def plot_with_mplfinance(df, patterns, specific_pattern=None):
    # Ensure no NaN values and alignment of indices and values
    if specific_pattern:
        pattern_points = patterns[specific_pattern].replace(0, pd.NA).dropna()
        apdict = mpf.make_addplot(pattern_points, type='scatter', markersize=100, marker='^', color='g')
    else:
        apdict = None

    # Create the plot
    mpf.plot(df, type='candle', addplot=apdict, style='charles', title=f"{specific_pattern} Pattern", ylabel="Price")


# Example usage in main section would remain the same


def plot_with_bokeh(df, patterns, specific_pattern=None):
    source = ColumnDataSource(df)
    p = figure(x_axis_type="datetime", title=f"Candlestick with {specific_pattern} markers")
    inc = df.close > df.open
    dec = df.open > df.close
    p.segment(df.index[inc], df.high[inc], df.index[inc], df.low[inc], color="green")
    p.segment(df.index[dec], df.high[dec], df.index[dec], df.low[dec], color="red")
    if specific_pattern:
        pattern_points = df[df.index.isin(patterns[patterns[specific_pattern] != 0].index)]
        p.circle(pattern_points.index, pattern_points.close, size=10, color="blue", legend_label=specific_pattern)
    show(p)




def plot_with_bokeh(df, patterns, specific_pattern=None):
    source = ColumnDataSource(df)
    p = figure(x_axis_type="datetime", title=f"Candlestick with {specific_pattern} markers")
    inc = df.close > df.open
    dec = df.open > df.close

    # Use segment to create the candlestick lines
    p.segment(df.index[inc], df.high[inc], df.index[inc], df.low[inc], color="green")
    p.segment(df.index[dec], df.high[dec], df.index[dec], df.low[dec], color="red")

    # Use scatter instead of circle
    if specific_pattern:
        pattern_points = df[df.index.isin(patterns[patterns[specific_pattern] != 0].index)]
        p.scatter(pattern_points.index, pattern_points.close, size=10, color="blue", marker="circle", legend_label=specific_pattern)

    show(p)


# Example usage
if __name__ == "__main__":
    symbol = "EURUSD=X"
    period = "1mo"
    interval = "1h"
    specific_pattern = 'CDLENGULFING'

    df = fetch_historical_data(symbol, period, interval)
    df = clean_data(df)
    patterns = identify_candlestick_patterns(df)

    # Plot using Plotly
    #plot_candlestick_chart(df, patterns, specific_pattern=specific_pattern)
    # Plot using mplfinance
    #plot_with_mplfinance(df, patterns, specific_pattern=specific_pattern)
    # Plot using Bokeh
    plot_with_bokeh(df, patterns, specific_pattern=specific_pattern)'''

# ----------------------------------------------------------------------------------------------------------------------------------------------------------

'''
def fetch_historical_data(symbol, period, interval):
    """
    Fetch historical data for a given symbol, period, and interval from yfinance.
    """
    try:
        df = yf.download(symbol, period=period, interval=interval)
        if df.empty:
            raise ValueError(f"No data returned for {symbol}.")
        df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Adj Close': 'adj close',
            'Volume': 'volume'
        }, inplace=True)
        #print(f"Data for {symbol} fetched successfully.")
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def clean_data(df):
    """
    Clean and prepare the fetched financial data.
    """
    required_columns = ['high', 'low', 'open', 'close', 'adj close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in DataFrame: {missing_columns}")
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    #print("Data cleaned successfully.")
    return df
'''
# -----------------------------------------------------------------------------------------------------------------------------------------------------

def fetch_historical_data(symbol, period, interval, timezone='Europe/London'):
    """
    Fetch historical data for a given symbol, period, and interval from yfinance.
    Automatically localize the time zone to the provided 'timezone'.
    """
    try:
        df = yf.download(symbol, period=period, interval=interval)
        if df.empty:
            raise ValueError(f"No data returned for {symbol}.")

        # Check if the index is already timezone aware and convert if not
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC').tz_convert(timezone)
        else:
            df.index = df.index.tz_convert(timezone)

        # Renaming columns to lower case
        df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Adj Close': 'adj close',
            'Volume': 'volume'
        }, inplace=True)

        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def clean_data(df):
    """
    Clean and prepare the fetched financial data.
    """
    if df is None:
        print("No data to clean, DataFrame is None.")
        return None

    required_columns = ['high', 'low', 'open', 'close', 'adj close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in DataFrame: {missing_columns}")

    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    return df

# -----------------------------------------------------------------------------------------------------------------------------------------------------
def identify_candlestick_patterns(df):
    """
    Identify candlestick patterns using TA-Lib and return a DataFrame with these patterns flagged.
    """
    pattern_functions = {name: func for name, func in talib.__dict__.items() if 'CDL' in name}
    pattern_data = []
    for name, func in pattern_functions.items():
        result = func(df['open'], df['high'], df['low'], df['close'])
        result_df = pd.DataFrame(result, index=df.index, columns=[name])
        pattern_data.append(result_df)
    patterns = pd.concat(pattern_data, axis=1)
    return patterns


def print_all_patterns(patterns):
    """
    Print all candlestick patterns that are present in the data.
    """
    for index, row in patterns.iterrows():
        found_patterns = [pattern for pattern, value in row.items() if value != 0]
        if found_patterns:
            print(f"{index}: {', '.join(found_patterns)}")


'''def print_specific_pattern(patterns, specific_pattern):
    """
    Print occurrences of a specific candlestick pattern. If no occurrences are found,
    print that no specific pattern was found. Additionally, trim 'CDL' from the start
    of the pattern name if it's a prefix.
    """
    found = False  # Flag to track if any specific pattern is found

    # Trim 'CDL' from the start of the pattern name if it's a prefix
    if specific_pattern.startswith('CDL'):
        trimmed_pattern_name = specific_pattern[3:]  # Assume 'CDL' is always the prefix
    else:
        trimmed_pattern_name = specific_pattern

    for index, row in patterns.iterrows():
        if row[specific_pattern] != 0 and row[specific_pattern] != -100:
            print(f"{index} - {trimmed_pattern_name}: {row[specific_pattern]}")
            found = True

    if not found:  # Check if the flag is still False after looping
        print(f"No '{trimmed_pattern_name}' was found during analysis.")
'''
def print_specific_pattern(patterns, specific_pattern):
    """
    Print the last 10 occurrences of a specific candlestick pattern. If fewer than 10 occurrences are found,
    print all of them. If no occurrences are found, print that no specific pattern was found.
    Additionally, trim 'CDL' from the start of the pattern name if it's a prefix.
    """
    found_trades = []  # List to store found trades

    # Trim 'CDL' from the start of the pattern name if it's a prefix
    if specific_pattern.startswith('CDL'):
        trimmed_pattern_name = specific_pattern[3:]  # Assume 'CDL' is always the prefix
    else:
        trimmed_pattern_name = specific_pattern

    # Iterate through the DataFrame rows
    for index, row in patterns.iterrows():
        if row[specific_pattern] != 0 and row[specific_pattern] != -100:
            found_trades.append(f"{index} - {trimmed_pattern_name}: {row[specific_pattern]}")

    # Check if we have any trades found
    if found_trades:
        # Print only the last 10 trades
        for trade in found_trades[-10:]:
            print(trade)
    else:
        print(f"No '{trimmed_pattern_name}' was found during analysis.")


def plot_candlestick_chart(df, patterns, specific_pattern=None):
    """
    Plot the candlestick chart using lightweight-charts and highlight patterns.
    """
    chart = Chart()
    chart.legend(visible=True)
    chart.set(df)
    chart.show(block=True)



def fetch_live_price(symbol):
    """
    Fetch the live price of the given symbol using yfinance.
    """
    stock = yf.Ticker(symbol)
    # Fetch data
    data = stock.history(period="1d")  # You can adjust the period and interval
    if not data.empty:
        last_close = data['Close'].iloc[-1]  # Get the last close price
        return last_close
    else:
        print(f"No data found for {symbol}")
        return None



# Example usage
if __name__ == "__main__":
    symbol = "EURUSD=X"
    period = "1mo"
    interval = "5m"
    specific_pattern = 'CDLDOJI'

    df = fetch_historical_data(symbol, period, interval)
    if df is not None:
        df = clean_data(df)
        patterns = identify_candlestick_patterns(df)
        print_specific_pattern(patterns, specific_pattern)  # To print a specific pattern
    else:
        print("Failed to fetch data.")

