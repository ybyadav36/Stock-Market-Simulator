import os
import time
import pymongo
import requests
import json
import pandas as pd
from pymongo import MongoClient

# Alpha Vantage API Key
api_key = os.getenv("VZ480LSCAC63VPLG")

# MongoDB Connection (using container name and port)
client = MongoClient('mongodb://localhost:27017/')  
db = client['my-mongodb-container']  # Database name

# Collection Creation (with error handling)
daily_collection = db['stock-prices-daily']
try:
    daily_collection.create_index([('symbol', 1)], unique=True)  # Ensure unique symbols
except pymongo.errors.CollectionInvalid:
    print("Collection 'stock-prices-daily' already exists.")

intraday_collection = db['stock-prices-intraday']
try:
    intraday_collection.create_index([('symbol', 1)], unique=True)  # Ensure unique symbols
except pymongo.errors.CollectionInvalid:
    print("Collection 'stock-prices-intraday' already exists.")

# Alpha Vantage API Endpoint for Daily Time Series Data
alpha_vantage_url_daily = "https://www.alphavantage.co/query"
symbol = "MSFT"  # Example symbol, can be changed
function = "TIME_SERIES_DAILY"
params = {
    "function": function,
    "symbol": symbol,
    "apikey": api_key,
}

# Alpha Vantage API Endpoint for Intraday Time Series Data
alpha_vantage_url_intraday = "https://www.alphavantage.co/query"
symbol = "MSFT"  # Example symbol, can be changed
function = "TIME_SERIES_INTRADAY"
interval = "1min"  # Interval can be changed to 5min, 15min, 30min, or 60min
params = {
    "function": function,
    "symbol": symbol,
    "interval": interval,
    "apikey": api_key,
}

# Rate limiting to 5 API calls per minute
time.sleep(12)  # Sleep for 12 seconds to ensure we don't exceed 5 API calls per minute

# Make API request to Alpha Vantage for Daily Time Series Data
response = requests.get(alpha_vantage_url_daily, params=params)

if response.status_code == 200:
    data = response.json().get("Time Series (Daily)")
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = 'date'
    df.reset_index(inplace=True)
    df['symbol'] = symbol
    df['type'] = 'daily'
    df.to_json('stock_prices.json', orient='records')

    # Insert data into MongoDB
    daily_collection.insert_many(df.to_dict('records'))

    # Rate limiting to 5 API calls per minute
    time.sleep(12)  # Sleep for 12 seconds to ensure we don't exceed 5 API calls per minute

    # Make API request to Alpha Vantage for Intraday Time Series Data
    response = requests.get(alpha_vantage_url_intraday, params=params)

    if response.status_code == 200:
        data = response.json().get("Time Series (1min)")
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index.name = 'timestamp'
        df.reset_index(inplace=True)
        df['symbol'] = symbol
        df['type'] = 'intraday'
        df.to_json('stock_prices.json', orient='records')

        # Insert data into MongoDB
        intraday_collection.insert_many(df.to_dict('records'))