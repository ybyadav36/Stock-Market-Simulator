import time
import logging
import requests
from confluent_kafka import Producer
import pandas as pd
from pymongo import MongoClient
import yaml
import os

# Alpha Vantage rate limit: 5 calls per minute
ALPHA_VANTAGE_RATE_LIMIT = 5
ALPHA_VANTAGE_TIME_INTERVAL = 60  # seconds
alpha_vantage_last_reset_time = time.time()
alpha_vantage_calls = 0

# Get the path to the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load configuration from config.yml in the root directory
config_file_path = os.path.join(root_dir, "config.yml")
with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Kafka Producer
kafka_producer_config = {
    'bootstrap.servers': config['development']['kafka']['bootstrap_servers'],
}

producer = Producer(kafka_producer_config)

def get_daily_data(symbol, outputsize='compact'):
    global alpha_vantage_calls, alpha_vantage_last_reset_time

    api_key = config['development']['api_keys']['alpha_vantage']
    base_url = 'https://www.alphavantage.co/query'
    function = 'TIME_SERIES_DAILY'

    current_time = time.time()
    time_since_last_reset = current_time - alpha_vantage_last_reset_time

    if time_since_last_reset < ALPHA_VANTAGE_TIME_INTERVAL:
        wait_time = ALPHA_VANTAGE_TIME_INTERVAL - time_since_last_reset
        logger.info(f"Waiting {wait_time} seconds before making the next Alpha Vantage request...")
        time.sleep(wait_time)

    params = {
        'function': function,
        'symbol': symbol,
        'outputsize': outputsize,
        'apikey': api_key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses

        data = response.json()

        if 'Time Series (Daily)' in data:
            # Extract daily data
            daily_data = data['Time Series (Daily)']
            df = pd.DataFrame(daily_data).T
            df.index = pd.to_datetime(df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']

            # Convert Timestamps to strings
            df.index = df.index.astype(str)

            # Increment the rate limit counter
            alpha_vantage_calls += 1

            # Reset the rate limit counter
            if alpha_vantage_calls >= ALPHA_VANTAGE_RATE_LIMIT:
                alpha_vantage_calls = 0
                alpha_vantage_last_reset_time = time.time()

            # Initialize MongoDB client
            client = MongoClient(config['development']['database']['mongodb']['uri'])
            MONGO_COLLECTION = "historical_data"

            # Save the fetched data in MongoDB
            db = client[config['development']['database']['mongodb']['db_name']]
            collection = db[MONGO_COLLECTION]  # Using collection name directly
            collection.insert_one({"symbol": symbol, "data": df.to_dict()})
            logger.info(f"Data for {symbol} saved to MongoDB.")

            # Send the fetched data to Kafka
            #send_to_kafka(topic=config['development']['kafka']['topic'], key=symbol, data=df)
            send_to_kafka(topic='historical-data', key=symbol, data=df)

            return df
        else:
            logger.error(f"Failed to fetch daily data for {symbol}. Response: {data}")
            return None
    except requests.RequestException as e:
        logger.error(f"Failed to make Alpha Vantage request: {e}")
        return None

def send_to_kafka(topic, key, data):
    try:
        # Convert DataFrame to JSON string before sending to Kafka
        json_data = data.to_json()

        # Send data to Kafka with a dynamic key (e.g., based on the symbol)
        producer.produce(topic, key=key, value=json_data)
        producer.flush()  # Ensure any outstanding messages are delivered
        logger.info(f"Data sent to Kafka topic '{topic}' successfully for symbol '{key}'.")
    except Exception as e:
        logger.error(f"Failed to send data to Kafka: {e}")

# Example usage:
symbols = ["AAPL", "GOOG", "META", "AMZN"]
for symbol in symbols:
    get_daily_data(symbol, outputsize='full')