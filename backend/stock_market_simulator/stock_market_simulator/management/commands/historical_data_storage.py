import time
import logging
import requests
from django.core.management.base import BaseCommand
import pandas as pd
from pymongo import MongoClient
from confluent_kafka import Producer
from Script.daily_stock_data import main as daily_stock_data_main
from django.conf import settings

class Command(BaseCommand):
    help = 'Fetch daily stock data and store it in MongoDB and Kafka'

    def handle(self, *args, **kwargs):
        # Call the daily_stock_data script
        daily_stock_data_main()

        # Initialize MongoDB client
        mongo_uri = settings.MONGO_URI
        client = MongoClient(mongo_uri)
        db = client[settings.MONGO_DB_NAME]
        collection = db[settings.MONGO_COLLECTION]

        # Initialize Kafka Producer
        kafka_producer_config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
        }
        producer = Producer(kafka_producer_config)

        # Alpha Vantage rate limit: 5 calls per minute
        alpha_vantage_rate_limit = settings.ALPHA_VANTAGE_RATE_LIMIT
        alpha_vantage_time_interval = settings.ALPHA_VANTAGE_TIME_INTERVAL
        alpha_vantage_last_reset_time = time.time()
        alpha_vantage_calls = 0

        symbols = settings.STOCK_SYMBOLS

        for symbol in symbols:
            data = get_daily_data(symbol)
            if data is not None:
                save_to_mongodb(collection, symbol, data)
                send_to_kafka(producer, symbol, data)

def get_daily_data(symbol, outputsize='compact'):
    api_key = settings.ALPHA_VANTAGE_API_KEY
    base_url = 'https://www.alphavantage.co/query'
    function = 'TIME_SERIES_DAILY'

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

            return df
        else:
            logging.error(f"Failed to fetch daily data for {symbol}. Response: {data}")
            return None
    except requests.RequestException as e:
        logging.error(f"Failed to make Alpha Vantage request: {e}")
        return None

def save_to_mongodb(collection, symbol, data):
    try:
        collection.insert_one({"symbol": symbol, "data": data.to_dict()})
        logging.info(f"Data for {symbol} saved to MongoDB.")
    except Exception as e:
        logging.error(f"Failed to save data to MongoDB: {e}")

def send_to_kafka(producer, symbol, data):
    try:
        # Convert DataFrame to JSON string before sending to Kafka
        json_data = data.to_json()

        # Send data to Kafka with a dynamic key (e.g., based on the symbol)
        producer.produce(topic='historical-data', key=symbol, value=json_data)
        producer.flush()  # Ensure any outstanding messages are delivered
        logging.info(f"Data sent to Kafka topic 'historical-data' successfully for symbol '{symbol}'.")
    except Exception as e:
        logging.error(f"Failed to send data to Kafka: {e}")
        
    symbols = ["AAPL", "GOOG", "META", "AMZN"]
    for symbol in symbols:
        get_daily_data(symbol, outputsize='full')           