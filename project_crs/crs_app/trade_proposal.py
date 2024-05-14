import pandas as pd
import yfinance as yf
# import talib
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py_off
from lightweight_charts import Chart
from tradingview_ta import TA_Handler, Interval, Exchange

# Plotting imports
import matplotlib.pyplot as plt
import mplfinance as mpf


def fetch_tradingview_indicators_summary(symbol):
    # Dictionary of symbols to handle different cases
    symbols = {'EURUSD=X': 'EURUSD', 'GBPUSD=X': 'GBPUSD',"GBPCHF=X" : "GBPCHF", "EURGBP=X" : "EURGBP",
               "AUDUSD=X" : "AUDUSD", "EURCHF=X" : "EURCHF"   ,'GOLD=X': 'GOLD'}


    # Determine the appropriate symbol key from the dictionary
    symbol_key = symbols.get(symbol, None)

    if symbol_key is None:
        print(f"No configuration for symbol {symbol}")
        return "NEUTRAL"

    # Initialize TA_Handler with dynamic symbol information
    handler = TA_Handler(
        symbol=symbol_key,
        screener="forex",
        exchange="FX_IDC",
        interval=Interval.INTERVAL_1_HOUR,
        timeout=None
    )

    # Get the analysis and summary recommendation
    analysis = handler.get_analysis()
    summary = analysis.summary
    recommendation = summary['RECOMMENDATION']

    # Determine action based on recommendation
    if recommendation in ['BUY', 'STRONG_BUY']:
        return 'Buy'
    elif recommendation in ['SELL', 'STRONG_SELL']:
        return 'Sell'
    elif recommendation == 'NEUTRAL':
        print('Neutral recommendation - Waiting for a clear trading signal...')

    return 'NEUTRAL'


def fetch_live_price(symbol):
    """
    Fetch the live price of the given symbol using yfinance.
    """
    stock = yf.Ticker(symbol)
    # Fetch data
    data = stock.history(period="2m")  # You can adjust the period and interval
    if not data.empty:
        last_close = data['Close'].iloc[-1]  # Get the last close price
        return last_close
    else:
        print(f"No data found for {symbol}")
        return None


def trade_proposal_live_price(symbol):

    live_price = fetch_live_price(symbol)
    signal_to_use = tradingview_signal = fetch_tradingview_indicators_summary(symbol)

    #print(f"Trade Proposal Live Price: {symbol}")

    # Check if live_price is valid
    if live_price is None or live_price <= 0:
        print(f"Invalid live price data for {symbol}.")
        return None

    if signal_to_use not in ['Buy', 'Sell']:
        raise ValueError("Its not a Good time to place a Trade our Signal is saying NEUTRAL.'")

    # print("\n🌟 Trade Generator Activated. 🌟")
    print(f"🌟 Trade Generator Activated. 🌟 ")

    # Assuming gold is traded in USD and the pip value for gold is 0.1
    pip_value = 0.001

    # Define the gap for stop loss and take profit
    stop_loss_gap = 20 * pip_value  # Example: 0.5 USD
    take_profit_gap = 40 * pip_value  # Example: 1.5 USD

    if signal_to_use == 'Buy':
        entry_price = live_price
        stop_loss = entry_price - stop_loss_gap  # Lower than entry for Buy
        take_profit = entry_price + take_profit_gap  # Higher than entry for Buy
    elif signal_to_use == 'Sell':
        entry_price = live_price
        stop_loss = entry_price + stop_loss_gap  # Higher than entry for Sell
        take_profit = entry_price - take_profit_gap  # Lower than entry for Sell

    # Create a trade proposal dictionary
    trade_proposal = {
        'Symbol': symbol,
        'Signal': signal_to_use,
        'Entry Price': entry_price,
        'Stop Loss': stop_loss,
        'Take Profit': take_profit
    }

    clean_symbol = symbol.replace('=X', '')  # This will remove '=X' from the symbol string

    # Print the trade proposal
    print("\n💡🔴🔴 Trade Proposal: 🔴🔴💡")
    print(f"Symbol: trade_proposal {clean_symbol}")
    print(f"Signal: {trade_proposal['Signal']}")
    print(f"Entry Price: {trade_proposal['Entry Price']}")
    print(f"Stop Loss: {trade_proposal['Stop Loss']}")
    print(f"Take Profit: {trade_proposal['Take Profit']}\n")

    return trade_proposal


# Example usage
if __name__ == "__main__":


    # Example usage
    try:
        trade_proposal_live_price(symbol=symbol)
    except Exception as e:
        print(e)


