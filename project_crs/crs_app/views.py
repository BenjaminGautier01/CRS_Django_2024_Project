from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.utils import IntegrityError
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from .models import CandlestickPattern
import io
import sys
from django.http import Http404



# ------------------------
import pandas as pd
import yfinance as yf
#import talib
import numpy as np
import plotly.graph_objects as go
import plotly.offline as py_off
from lightweight_charts import Chart
# Plotting imports
import matplotlib.pyplot as plt
import mplfinance as mpf


from .candles import fetch_historical_data, clean_data, identify_candlestick_patterns, plot_candlestick_chart
from .candles import print_specific_pattern
from .trade_proposal import fetch_tradingview_indicators_summary,fetch_live_price,trade_proposal_live_price
from .models import Message  # Make sure to import your Message model
from .models import CandlestickPattern



# Create your views here.
def index(request):
    return render(request, 'index.html')

def leave_message(request):

    if request.method == 'POST':
        try:
            # Retrieve data from POST request
            full_name = request.POST.get('full_name')
            phone_number = request.POST.get('phone_number')
            email_address = request.POST.get('email')  # Make sure to use the correct field name as in your HTML form
            user_message = request.POST.get('message')  # Renamed variable to avoid confusion with the model

            try:
                # Create a new Message object and save it to the database
                new_message = Message.objects.create(
                    full_name=full_name,
                    phone_number=phone_number,
                    email=email_address,
                    message=user_message
                )
                new_message.save()

                # If save is successful, display a success message and redirect
                messages.success(request, "Message sent successfully. We will get in touch shortly. Thank you!")

                return redirect('index')  # Ensure 'index' is the name of the URL to redirect to

            except IntegrityError:
                # If an IntegrityError occurred, display an error message and reload the form
                messages.error(request, "Error sending message. Please try again.")
                return render(request, 'index.html')
        except ValueError as e:
            return render(request, 'error_page.html', {'error_message': str(e)})


    # For GET requests, just display the form
    return render(request, 'index.html')



def signup(request):
    if request.method == 'POST':
        try:

            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('password1')

            # Check if the email already exists
            if User.objects.filter(username=email).exists():
                messages.error(request, "Email already in use.")
                return render(request, 'signup.html')

            # Check if the passwords match
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'signup.html')

            try:
                # Create new user if the email is unique and passwords match
                user = User.objects.create_user(username=email, email=email, password=password)
                user.first_name = first_name
                user.last_name = last_name
                user.save()

                # Optionally log the user in after signing up
                login(request, user)
                messages.success(request, "Registration successful. You can now sign in.")
                return redirect('signin')  # Redirect to a new URL if registration is successful
            except IntegrityError:
                messages.error(request, "Error creating user. Please try again.")
                return render(request, 'signup.html')

        except ValueError as e:
            # Handle the error gracefully
            return render(request, 'error_page.html', {'error_message': str(e)})

    return render(request, 'signup.html')


def signin(request):
    context = {}  # Initialize context dictionary properly
    if request.method == 'POST':
        try:

            email = request.POST.get('email')  # Get the email input
            password = request.POST.get('password')  # Get the password input

            # Authenticate the user
            user = authenticate(request, username=email, password=password)


            if user is not None:
                # User is successfully authenticated, get the full name
                full_name = f"{user.first_name} {user.last_name}".strip()



                request.session['user_name'] = full_name  # Store the name in session
                login(request, user)  # Log the user in
                messages.success(request, f'Welcome {full_name}')
                return redirect('dashboard')  # Redirect to dashboard view if login is successful
            else:
                messages.error(request, 'Invalid credentials')
                return redirect('signin')

                # Get the user's first name if the user is authenticated
            if request.user.is_authenticated:
                context['name'] = request.user.first_name

        except ValueError as e:
            # Handle the error gracefully
            return render(request, 'error_page.html', {'error_message': str(e)})
    return render(request, 'signin.html', context)  # Pass context to the template


def dashboard(request):
    context = {}
    if request.method == 'POST':

        try:
            # Handle data fetching and processing
            symbol_choice = request.POST.get('symbol_choice')
            pattern_choice = request.POST.get('pattern_choice')
            interval_choice = request.POST.get('interval_choice', '15m')

            # Capture printed output
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()

            # Data processing (assuming these functions are defined elsewhere)
            df = fetch_historical_data(symbol_choice, '1mo', interval_choice)
            df = clean_data(df)
            patterns = identify_candlestick_patterns(df)
            print_specific_pattern(patterns, pattern_choice)

            sys.stdout = old_stdout
            context['dashboard_results'] = redirected_output.getvalue()

            # Handle pattern fetching
            try:
                # Fetch the pattern by name, ignoring case
                pattern = CandlestickPattern.objects.get(candlestick_pattern_name__iexact=pattern_choice)

                # Trim 'CDL' from the start of the pattern name if it's a prefix
                if pattern.candlestick_pattern_name.startswith('CDL'):
                    trimmed_pattern_name = pattern.candlestick_pattern_name[3:]  # Assume 'CDL' is always the prefix
                else:
                    trimmed_pattern_name = pattern.candlestick_pattern_name

                # Store the pattern's details in context
                context['pattern_name'] = trimmed_pattern_name
                context['pattern_image'] = pattern.candlestick_image
                context['pattern_text'] = pattern.candlestick_pattern_text

            except CandlestickPattern.DoesNotExist:
                # Handle the case where the pattern does not exist
                text = ' Pattern  Not Found During Analysis.'
                context['error'] = text
                # Optional: Redirect to the dashboard or another appropriate page
                # return redirect('dashboard')

            # Add the user's first name if authenticated
            if request.user.is_authenticated:
                # Access user's first name and last name
                user_first_name = request.user.first_name
                user_last_name = request.user.last_name

                # Add the names to the context
                context['user_first_name'] = user_first_name
                context['user_last_name'] = user_last_name
                context['interval_choice'] = interval_choice
                clean_symbol = symbol_choice.replace('=X', '')  # This will remove '=X' from the symbol string
                context['symbol_choice']= clean_symbol

                # You can also concatenate and send the full name
                context['user_full_name'] = f"{user_first_name} {user_last_name}"

        except ValueError as e:
            # Handle the error gracefully
            return render(request, 'error_page.html', {'error_message': str(e)})

    return render(request, 'dashboard.html', context)


def chart_view(request):
    return render(request, 'dashboard.html')

'''def dashboard(request):
    context = {}
    if request.method == 'POST':
        # Sample data fetching and processing
        symbol_choice = request.POST.get('symbol_choice', 'EURUSD=X')
        pattern_choice = request.POST.get('pattern_choice', 'CDLHAMMER')
        interval_choice = request.POST.get('interval_choice', '5m')

        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        # Imagine these functions fetch and process data
        df = fetch_historical_data(symbol_choice, '1mo', interval_choice)
        df = clean_data(df)
        patterns = identify_candlestick_patterns(df)
        print_specific_pattern(patterns, pattern_choice)
        #plot_candlestick_chart(df, patterns, specific_pattern=pattern_choice)

        sys.stdout = old_stdout
        context['dashboard_results'] = redirected_output.getvalue()

    return render(request, 'dashboard.html', context)'''

def print_patterns(request):
    context = {}
    if request.method == 'POST':
        try:
            # Retrieving user selections from the form in the POST request
            symbol_choice = request.POST.get('symbol_choice', 'EURUSD=X')
            pattern_choice = request.POST.get('pattern_choice', 'No Pattern Found!')
            interval_choice = request.POST.get('interval_choice', '5m')

            # Redirecting stdout to capture function outputs
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()

            # Processing data based on user inputs
            df = fetch_historical_data(symbol_choice, '1mo', interval_choice)
            if df is not None:
                df = clean_data(df)
                patterns = identify_candlestick_patterns(df)
                print_specific_pattern(patterns, pattern_choice)
                # plot_candlestick_chart(df, patterns, specific_pattern=pattern_choice)

            sys.stdout = old_stdout
            context['symbol_choice'] = symbol_choice
            context['interval_choice'] = interval_choice
            context['print_results'] = redirected_output.getvalue()

        except Exception as e:  # Catching all exceptions to handle unexpected errors
            context['error_message'] = str(e)
            return render(request, 'error_page.html', context)

    # Returning data to the dashboard template
    return render(request, 'dashboard.html', context)


def plot_chart(request):
    context = {}
    print("dashboard1 is being called")  # This will print in your console
    if request.method == 'POST':

        try:

            # Fetching and processing data based on POST data
            symbol_choice = request.POST.get('symbol_choice', 'EURUSD=X')
            pattern_choice = request.POST.get('pattern_choice', 'CDLHAMMER')
            interval_choice = request.POST.get('interval_choice', '5m')

            # Redirect output to capture for display
            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()

            # Data processing functions
            df = fetch_historical_data(symbol_choice, '1mo', interval_choice)
            df = clean_data(df)
            patterns = identify_candlestick_patterns(df)
            plot_candlestick_chart(df, patterns, specific_pattern=pattern_choice)

            clean_symbol = symbol_choice.replace('=X', '')

            # Capture output and reset standard output
            sys.stdout = old_stdout
            context['plot_chart_results'] = redirected_output.getvalue()
            context['clean_symbol'] = symbol_choice  # Save symbol_choice to context to use in the template

        except ValueError as e:
            # Handle the error gracefully
            return render(request, 'error_page.html', {'error_message': str(e)})
    return render(request, 'dashboard.html', context)

'''
def fetch_pattern(request):
    context = {}

    if request.method == 'POST':
        # Get the chosen pattern name from POST data, defaulting to a common pattern if not provided
        chosen_pattern_name = request.POST.get('pattern_choice', 'CDLENGULFING')

        # Try to get the pattern directly from the database using the provided name
        try:
            pattern = CandlestickPattern.objects.get(candlestick_pattern_name__iexact=chosen_pattern_name)
            context['pattern_name'] = pattern.candlestick_pattern_name  # Store the pattern's name
            context['pattern_image'] = pattern.candlestick_image        # Store the pattern's image
            context['pattern_name'] = pattern.candlestick_pattern_text  # Store the pattern's text
        except CandlestickPattern.DoesNotExist:
            # If no pattern is found, handle this case by showing an error message
            messages.error(request, "The selected pattern was not found.")
            return render(request, 'dashboard.html', context)

    # If it's not a POST request or after handling POST
    return render(request, 'dashboard.html', context)'''


def trade_proposal(request):
    context = {}
    if request.method == 'POST':
        try:

            #  data fetching and processing
            trade_proposal_symbol_choice = request.POST.get('symbol_choice', 'CDLENGULFING')
            pattern_choice = request.POST.get('pattern_choice', 'CDLHAMMER')
            interval_choice = request.POST.get('interval_choice', '5m')

            old_stdout = sys.stdout
            redirected_output = sys.stdout = io.StringIO()

            trade_proposal_result = trade_proposal_live_price(trade_proposal_symbol_choice)

            #print("This is the Trade proposal section!")
            #print_specific_pattern(patterns, pattern_choice)
            #plot_candlestick_chart(df, patterns, specific_pattern=pattern_choice)

            sys.stdout = old_stdout
            trade_proposal_symbol_choice1 = trade_proposal_symbol_choice.replace('=X', '')
            context['trade_proposal_results'] = redirected_output.getvalue()
            context['trade_proposal_symbol_choice'] = trade_proposal_symbol_choice1  # Save symbol_choice to context to use in the template

        except ValueError as e:
            # Handle the error gracefully
            return render(request, 'error_page.html', {'error_message': str(e)})

    return render(request, 'dashboard.html', context)







patterns = {
    'CDL2CROWS': 'Two Crows',
    'CDL3BLACKCROWS': 'Three Black Crows',
    'CDL3INSIDE': 'Three Inside Up / Down',
    'CDL3LINESTRIKE': 'Three - Line Strike',
    'CDL3OUTSIDE': 'Three Outside Up / Down',
    'CDL3STARSINSOUTH': 'Three Stars In The South',
    'CDL3WHITESOLDIERS': 'Three Advancing White Soldiers',
    'CDLABANDONEDBABY': 'Abandoned Baby',
    'CDLADVANCEBLOCK': 'Advance Block',
    'CDLBELTHOLD': 'Belt - hold',
    'CDLBREAKAWAY': 'Breakaway',
    'CDLCLOSINGMARUBOZU': 'Closing Marubozu',
    'CDLCONCEALBABYSWALL': 'Concealing Baby Swallow',
    'CDLCOUNTERATTACK': 'Counterattack',
    'CDLDARKCLOUDCOVER': 'Dark Cloud Cover',
    'CDLDOJI': 'Doji',
    'CDLDOJISTAR': 'Doji Star',
    'CDLDRAGONFLYDOJI': 'Dragonfly Doji',
    'CDLENGULFING': 'Engulfing Pattern',
    'CDLEVENINGDOJISTAR': 'Evening Doji Star',
    'CDLEVENINGSTAR': 'Evening Star',
    'CDLGRAVESTONEDOJI': 'Gravestone Doji',
    'CDLHAMMER': 'Hammer',
    'CDLHANGINGMAN': 'Hanging Man',
    'CDLHARAMI': 'Harami Pattern',
    'CDLHARAMICROSS': 'Harami Cross Pattern',
    'CDLHIGHWAVE': 'High - Wave Candle',
    'CDLHIKKAKE': 'Hikkake Pattern',
    'CDLHIKKAKEMOD': 'Modified Hikkake Pattern',
    'CDLHOMINGPIGEON': 'Homing Pigeon',
    'CDLIDENTICAL3CROWS': 'Identical Three Crows',
    'CDLINNECK': 'In - Neck Pattern',
    'CDLINVERTEDHAMMER': 'Inverted Hammer',
    'CDLKICKING': 'Kicking',
    'CDLLADDERBOTTOM': 'Ladder Bottom',
    'CDLLONGLEGGEDDOJI': 'Long Legged Doji',
    'CDLLONGLINE': 'Long Line Candle',
    'CDLMARUBOZU': 'Marubozu',
    'CDLMATCHINGLOW': 'Matching Low',
    'CDLMATHOLD': 'Mat Hold',
    'CDLMORNINGDOJISTAR': 'Morning Doji Star',
    'CDLMORNINGSTAR': 'Morning Star',
    'CDLONNECK': 'On - Neck Pattern',
    'CDLPIERCING': 'Piercing Pattern',
    'CDLRICKSHAWMAN': 'Rickshaw Man',
    'CDLSEPARATINGLINES': 'Separating Lines',
    'CDLSHOOTINGSTAR': 'Shooting Star',
    'CDLSHORTLINE': 'Short Line Candle',
    'CDLSPINNINGTOP': 'Spinning Top',
    'CDLSTALLEDPATTERN': 'Stalled Pattern',
    'CDLSTICKSANDWICH': 'Stick Sandwich'
}


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def do(request):
    return render(request, 'do.html')