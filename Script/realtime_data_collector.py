from datetime import datetime, timedelta
from kafka import KafkaProducer
import yfinance as yf
import json
import time
from pytz import timezone

# Kafka configuration
kafka_producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)
kafka_topic = "stock-data"

# Symbols to track
symbols = ["AAPL", "GOOG", "META", "AMZN"]

# Set IST timezone
ist_timezone = timezone('Asia/Kolkata')

while True:
    try:
        # Get current start time in IST for the 30-second interval
        start_time_ist = datetime.now(ist_timezone)

        # Check if within desired market hours (7:00 PM to 2:30 AM IST)
        current_time_ist = start_time_ist.strftime("%H:%M:%S")
        if current_time_ist >= "19:00:00" and current_time_ist <= "02:30:00":
            # Run loop for the 30-second interval in IST, fetching and sending data
            for symbol in symbols:
                try:
                    # Download intraday data for the current minute in IST
                    current_time_ist = datetime.now(ist_timezone).strftime("%H:%M:%S")
                    today = datetime.now(ist_timezone).strftime("%Y-%m-%d")

                    # Adjust for US market time (9:30 AM EST onwards)
                    # Calculate time difference between IST and EST
                    est_timezone = timezone('America/New_York')
                    time_diff = est_timezone.localize(datetime.now()) - ist_timezone.localize(datetime.now())
                    est_current_time = (current_time_ist - time_diff).strftime("%H:%M:%S")

                    data = yf.download(
                        symbol,
                        start=f"{today} {est_current_time}",
                        end=f"{today} {est_current_time}",
                        interval="1m",
                    )

                    # Check if data is empty
                    if data.empty:
                        print(f"No data available for {symbol} at {est_current_time} EST, skipping...")
                        continue

                    # Create message dictionary
                    message = {
                        "symbol": symbol,
                        "timestamp": data.index[0].strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "data": data.to_dict("records"),
                    }

                    # Send message to Kafka
                    kafka_producer.send(kafka_topic, json.dumps(message))
                    print(f"Sent data for {symbol} at {est_current_time} EST to Kafka")

                except Exception as e:
                    if "out of bounds" in str(e):
                        print(f"Error fetching data for {symbol}: empty data, skipping...")
                    else:
                        print(f"Error fetching data for {symbol}: {e}")

                # Sleep for 30 seconds before fetching the next data
                time.sleep(30)

        else:
            print("Market is closed in IST, skipping data download...")

    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(60 * 5)  # Wait 5 minutes before retrying

# Flush and close producer (if you intend to stop the script manually)
kafka_producer.flush()