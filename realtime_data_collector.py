import requests
from datetime import datetime
from pymongo import MongoClient

# Alpha Vantage API Key
alpha_vantage_api_key = "Q1UJ6MLZ7CHJJ4E1"

# MongoDB Connection
client = MongoClient('mongodb://admin:ybyadav36-20April98@#$@localhost:27017/')
db = client['mydatabase']
collection = db['stock_prices']

# Alpha Vantage API Endpoint for Real-time Stock Quotes
alpha_vantage_url = "https://www.alphavantage.co/query"
symbol = "AAPL"
function = "GLOBAL_QUOTE"
params = {
    "function": function,
    "symbol": symbol,
    "apikey": alpha_vantage_api_key,
}

# Make API request to Alpha Vantage
response = requests.get(alpha_vantage_url, params=params)

if response.status_code == 200:
    data = response.json().get("Global Quote", {})
    
    # Insert data into MongoDB
    data['timestamp'] = datetime.now()
    result = collection.insert_one(data)
    
    # Print the ObjectId of the inserted document
    print(f"Document inserted with ObjectId: {result.inserted_id}")
else:
    print(f"Error fetching data from Alpha Vantage. Status code: {response.status_code}")

# Close MongoDB connection
client.close()