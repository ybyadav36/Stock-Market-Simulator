import time
import logging
import requests
from alpha_vantage.timeseries import TimeSeries
from pymongo import MongoClient
import pandas as pd

# Alpha Vantage rate limit: 5 calls per minute
ALPHA_VANTAGE_RATE_LIMIT = 5
ALPHA_VANTAGE_TIME_INTERVAL = 60  # seconds

# MongoDB connection
MONGODB_URI = 'mongodb://localhost:27017/'  # Update with your MongoDB connection URI
DB_NAME = 'my-mongodb-container'  # Update with your MongoDB database name
COLLECTION_NAME = 'stock_prices'

# Initialize variables for rate limiting
alpha_vantage_calls = 0
alpha_vantage_last_reset_time = time.time()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_daily_data(symbol, outputsize='compact'):
    api_key = 'Q1UJ6MLZ7CHJJ4E1'
    base_url = 'https://www.alphavantage.co/query'
    function = 'TIME_SERIES_DAILY'

    params = {
        'function': function,
        'symbol': symbol,
        'outputsize': outputsize,
        'apikey': api_key
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if 'Time Series (Daily)' in data:
        # Extract daily data
        daily_data = data['Time Series (Daily)']
        df = pd.DataFrame(daily_data).T
        df.index = pd.to_datetime(df.index)
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        return df
    else:
        print(f"Failed to fetch daily data for {symbol}.")
        return None

def make_alpha_vantage_api_call_and_store(ts, symbol, outputsize='compact'):
    global alpha_vantage_calls
    global alpha_vantage_last_reset_time

    # Check if we've reached the rate limit
    elapsed_time = time.time() - alpha_vantage_last_reset_time
    if alpha_vantage_calls >= ALPHA_VANTAGE_RATE_LIMIT and elapsed_time < ALPHA_VANTAGE_TIME_INTERVAL:
        wait_time = ALPHA_VANTAGE_TIME_INTERVAL - elapsed_time
        logger.warning(f"Rate limit reached. Waiting for {wait_time:.2f} seconds before making the next API call.")
        time.sleep(wait_time)

    # Make the API call
    for attempt in range(1, 4):  # 3 attempts
        try:
            data = get_daily_data(symbol, outputsize=outputsize)
            alpha_vantage_calls += 1

            # Check if a new minute has started
            if elapsed_time >= ALPHA_VANTAGE_TIME_INTERVAL:
                alpha_vantage_calls = 1
                alpha_vantage_last_reset_time = time.time()

            # Store data in MongoDB
            store_data_in_mongodb(data, symbol)

            return data
        except Exception as e:
            logger.error(f"API call failed on attempt {attempt}: {e}")
            if attempt < 3:
                logger.info(f"Retrying in 5 seconds...")
                time.sleep(5)
            else:
                logger.warning("Maximum retries reached. API call failed.")
                return None

def store_data_in_mongodb(data, symbol):
    try:
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Check if the data is in the correct format
        if data is not None:
            # Convert timestamps to string before storing in MongoDB
            data_str_timestamp = {str(key): value for key, value in data.to_dict(orient='index').items()}

            # Unpack the data and insert into MongoDB
            collection.insert_one({
                'symbol': symbol,
                'data': data_str_timestamp
            })
            logger.info(f"Data for {symbol} successfully stored in MongoDB.")
        else:
            logger.error(f"Invalid data format. Failed to store data in MongoDB for {symbol}.")
    except Exception as e:
        logger.error(f"Failed to store data in MongoDB: {e}")
    finally:
        # Close the MongoDB connection
        client.close()

# Example usage with multiple symbols:
symbols = ["AAPL", "GOOGL"]
ts = TimeSeries(key='Q1UJ6MLZ7CHJJ4E1', output_format='pandas')

for symbol in symbols:
    # Fetch daily data with rate limiting and store in MongoDB
    data = make_alpha_vantage_api_call_and_store(ts, symbol, outputsize='full')
    if data is not None:
        print(f"Data for {symbol}:")
        print(data)
    else:
        print(f"Failed to fetch and store daily data for {symbol}.")