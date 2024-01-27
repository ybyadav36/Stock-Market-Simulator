import requests
from pymongo import MongoClient

# Alpha Vantage API Key
alpha_vantage_api_key = "your_alpha_vantage_api_key"

# MongoDB Connection
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["your_mongo_database"]
collection = db["realtime_data"]

# Alpha Vantage API Endpoint for Real-time Stock Quotes
alpha_vantage_url = "https://www.alphavantage.co/query"
symbol = "AAPL"
interval = "1min"
function = "TIME_SERIES_INTRADAY"
params = {
    "function": function,
    "symbol": symbol,
    "interval": interval,
    "apikey": alpha_vantage_api_key,
}

response = requests.get(alpha_vantage_url, params=params)
data = response.json()["Time Series (1min)"]

# Store Data in MongoDB
for timestamp, values in data.items():
    document = {
        "timestamp": timestamp,
        "symbol": symbol,
        "open": float(values["1. open"]),
        "high": float(values["2. high"]),
        "low": float(values["3. low"]),
        "close": float(values["4. close"]),
        "volume": int(values["5. volume"]),
    }
    collection.insert_one(document)