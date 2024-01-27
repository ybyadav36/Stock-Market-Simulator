import requests
import psycopg2
from datetime import datetime

# Alpha Vantage API Key
alpha_vantage_api_key = "your_alpha_vantage_api_key"

# PostgreSQL Connection
conn = psycopg2.connect(
    database="your_postgres_database",
    user="your_postgres_user",
    password="your_postgres_password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Alpha Vantage API Endpoint for Historical Stock Quotes
alpha_vantage_url = "https://www.alphavantage.co/query"
symbol = "AAPL"
function = "TIME_SERIES_DAILY"
params = {
    "function": function,
    "symbol": symbol,
    "apikey": alpha_vantage_api_key,
}

response = requests.get(alpha_vantage_url, params=params)
data = response.json()["Time Series (Daily)"]

# Store Data in PostgreSQL
for date, values in data.items():
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    cur.execute(
        "INSERT INTO historical_stock_data (symbol, date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (symbol, date_obj, float(values["1. open"]), float(values["2. high"]), float(values["3. low"]), float(values["4. close"]), int(values["5. volume"]))
    )

conn.commit()
cur.close()
conn.close()