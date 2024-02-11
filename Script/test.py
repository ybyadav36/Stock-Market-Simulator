import time
import logging
import requests
from confluent_kafka import Producer, KafkaError
import pandas as pd
from pymongo import MongoClient

# Alpha Vantage API configuration
ALPHA_VANTAGE_API_KEY = 'Q1UJ6MLZ7CHJJ4E1'
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
ALPHA_VANTAGE_FUNCTION = 'TIME_SERIES_DAILY'
ALPHA_VANTAGE_OUTPUTSIZE = 'full'  # Fetch complete daily data
ALPHA_VANTAGE_RATE_LIMIT = 25
ALPHA_VANTAGE_TIME_INTERVAL = 60   # Seconds for 5 calls/day

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'stock-data'

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "your-mongodb-database"
MONGO_COLLECTION = "daily_stock_data"

# Kafka producer configuration
kafka_producer_config = {
    'bootstrap.servers': KAFKA_BROKER,
}
producer = Producer(kafka_producer_config)

# Global variables to track API calls
alpha_vantage_calls = 0
alpha_vantage_last_reset_time = time.time()

def get_daily_data(symbol):
    global alpha_vantage_calls, alpha_vantage_last_reset_time

    # Check if daily limit has been reached
    if alpha_vantage_calls >= ALPHA_VANTAGE_RATE_LIMIT:
        logging.info(f"Daily API call limit reached. Skipping {symbol}.")
        return None

    # Check if enough time has passed since last reset
    current_time = time.time()
    time_since_last_reset = current_time - alpha_vantage_last_reset_time

    # Calculate wait time and sleep if necessary
    if time_since_last_reset < ALPHA_VANTAGE_TIME_INTERVAL:
        wait_time = ALPHA_VANTAGE_TIME_INTERVAL - time_since_last_reset
        logging.info(f"Waiting {wait_time} seconds before making the next Alpha Vantage request...")
        time.sleep(wait_time)

    # Construct API URL
    params = {
        'function': ALPHA_VANTAGE_FUNCTION,
        'symbol': symbol,
        'outputsize': ALPHA_VANTAGE_OUTPUTSIZE,
        'apikey': ALPHA_VANTAGE_API_KEY,
    }
    url = ALPHA_VANTAGE_BASE_URL + ''.join(['?' + key + '=' + value for key, value in params.items()])

    # Make API call and handle errors
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()

        if 'Time Series (Daily)' in data:
            # Extract and format daily data
            daily_data = data['Time Series (Daily)']
            df = pd.DataFrame(daily_data).T
            df.index = pd.to_datetime(df.index)
            df.columns = ['open', 'high', 'low', 'close', 'volume']

            # Convert timestamps to strings for MongoDB
            df.index = df.index.astype(str)

            # Store data in MongoDB
            client = MongoClient(MONGO_URI)
            db = client[MONGO_DB]
            collection = db[MONGO_COLLECTION]
            collection.insert_one({"symbol": symbol, "data": df.to_dict()})
            logging.info(f"Data for {symbol} saved to MongoDB.")

            # Send data to Kafka (convert df to JSON string)
            send_to_kafka(topic=KAFKA_TOPIC, key=symbol, data=df.to_json())

            # Update call count and reset time
            alpha_vantage_calls += 1
            alpha_vantage_last_reset_time = current_time  # Always reset time after a call

            return df
        else:
            logging.error(f"Failed to fetch daily data for {symbol}. Response: {data}")
            return None
    except requests.RequestException as e:
        logging.error(f"Failed to make Alpha Vantage request: {e}")
        return None

def send_to_kafka(topic, key, data):
    try:
        producer.produce(topic, key=key, value=data)
        producer.poll(0)  # Poll for delivery status immediately
        if producer.delivery_report():  # Check for any delivery errors
            msg = producer.delivery_report()[0]
            if msg.error():
                logging.error(f"Error sending message to Kafka: {msg.error()}")
            else:
                logging.info(f"Data sent to Kafka topic '{topic}' for key '{key}' successfully.")
    except KafkaError as e:
        logging.error(f"Failed to send data to Kafka: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Example usage:
symbols = ["NIFTY 50", "Nifty Bank"]
for symbol in symbols:
    get_daily_data(symbol)
