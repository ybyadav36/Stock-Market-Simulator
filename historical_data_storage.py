import requests
import psycopg2
from datetime import datetime

# Alpha Vantage API Key
alpha_vantage_api_key = "Q1UJ6MLZ7CHJJ4E1"

# PostgreSQL Connection
conn = psycopg2.connect(
    database="Simulator",
    user="ybyadav36",
    password="20April98@#$",
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

# Create historical_stock_data table if not exists
cur.execute('''
    CREATE TABLE IF NOT EXISTS historical_stock_data (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10),
        date DATE,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume INT
    )
''')

# Make API request to Alpha Vantage
response = requests.get(alpha_vantage_url, params=params)

if response.status_code == 200:
    data = response.json().get("Time Series (Daily)", {})
    
    # Insert data into PostgreSQL
    records_inserted = 0
    for date, values in data.items():
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        cur.execute(
            "INSERT INTO historical_stock_data (symbol, date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (symbol, date_obj, float(values["1. open"]), float(values["2. high"]), float(values["3. low"]), float(values["4. close"]), int(values["5. volume"]))
        )
        records_inserted += 1

    # Commit changes
    conn.commit()
    
    # Print the total number of records inserted
    print(f"Total records inserted: {records_inserted}")
else:
    print(f"Error fetching data from Alpha Vantage. Status code: {response.status_code}")

# Close database connection
cur.close()
conn.close()
