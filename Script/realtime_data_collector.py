from datetime import datetime, timedelta
from pytz import timezone
import time
import json
from kafka import KafkaProducer
import yfinance as yf

# Kafka configuration
kafka_producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)
kafka_topic = "stock-data"

# Symbols to track
symbols = ["AAPL", "GOOG", "META", "AMZN"]

# Set US Eastern Timezone
us_eastern_timezone = timezone('US/Eastern')

while True:
    try:
        # Get current time in US Eastern Time
        current_time_us_eastern = datetime.now(us_eastern_timezone)

        # Check if within desired market hours (9:30 AM to 4:00 PM US Eastern Time)
        if current_time_us_eastern.hour >= 9 and current_time_us_eastern.hour < 16:
            for symbol in symbols:
                try:
                    # Fetch live data for the current minute
                    data = yf.download(
                        symbol,
                        period="1d",    # Fetch live data for the current day
                        interval="1m",  # 1-minute intervals
                    )

                    # Check if data is empty
                    if data.empty:
                        print(f"No data available for {symbol} at {current_time_us_eastern}, skipping...")
                        continue

                    # Create message dictionary
                    message = {
                        "symbol": symbol,
                        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "data": data.iloc[-1:].to_dict("records"),  # Fetch only the latest data point
                    }

                    # Send message to Kafka
                    kafka_producer.send(kafka_topic, json.dumps(message))
                    print(f"Sent data for {symbol} at {current_time_us_eastern} to Kafka")

                except Exception as e:
                    print(f"Error fetching data for {symbol}: {e}")

        else:
            print("US market is closed, skipping data download...")

        # Sleep for 30 seconds before fetching the next data
        time.sleep(30)

    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(60 * 5)  # Wait 5 minutes before retrying

# Flush and close producer (if you intend to stop the script manually)
kafka_producer.flush()