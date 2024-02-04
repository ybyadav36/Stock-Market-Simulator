import time
import logging
import requests
from confluent_kafka import Producer, KafkaError
import pandas as pd
from pymongo import MongoClient

# Alpha Vantage rate limit: 5 calls per minute
ALPHA_VANTAGE_RATE_LIMIT = 5
ALPHA_VANTAGE_TIME_INTERVAL = 60  # seconds

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'  # Update with your Kafka broker details
KAFKA_TOPIC = 'stock-data'  # Update with your Kafka topic name

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "my-mongodb-container"
MONGO_COLLECTION = "daily_stock_data"

# Initialize variables for rate limiting
alpha_vantage_calls = 0
alpha_vantage_last_reset_time = time.time()

# Initialize Kafka Producer
kafka_producer_config = {
    'bootstrap.servers': KAFKA_BROKER,
}

producer = Producer(kafka_producer_config)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_daily_data(symbol, outputsize='compact'):
    global alpha_vantage_calls, alpha_vantage_last_reset_time

    api_key = '1DMX8XAI11JYVQC5'
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
            client = MongoClient(MONGO_URI)

            # Save the fetched data in MongoDB
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            collection.insert_one({"symbol": symbol, "data": df.to_dict()})
            logger.info(f"Data for {symbol} saved to MongoDB.")

            # Send the fetched data to Kafka
            send_to_kafka(topic=KAFKA_TOPIC, key=symbol, data=df)

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
symbols = ["AAPL", "GOOGL"]
for symbol in symbols:
    get_daily_data(symbol, outputsize='full')