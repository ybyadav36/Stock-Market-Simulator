import json
import yfinance as yf
import pandas as pd
import psycopg2
from psycopg2 import OperationalError
import os
import yaml
import logging
import re

# Get the path to the root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load configuration from config.yml in the root directory
config_file_path = os.path.join(root_dir, "config.yml")
with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL connection parameters
pg_config = config['development']['database']['postgresql']

def connect_to_postgres():
    """Connect to PostgreSQL database."""
    try:
        pg_config = config.get('development', {}).get('database', {}).get('postgresql')
        if pg_config is None:
            raise ValueError("PostgreSQL configuration not found in config.yml")

        # Construct the DSN (Data Source Name) for connecting to PostgreSQL
        dsn = f"dbname={pg_config['db_name']} user={pg_config.get('username', '')} password={pg_config.get('password', '')} host={pg_config['host']} port={pg_config['port']}"
        
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
        return conn
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def table_exists(cursor, symbol):
    """Check if the table already exists."""
    cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE LOWER(table_name) = LOWER('{symbol}'))")
    return cursor.fetchone()[0]

def create_table(conn, symbol):
    """Create a table for storing historical data if it does not already exist."""
    sanitized_symbol = re.sub(r'\W+', '_', symbol.lower())  # Convert symbol to lowercase and replace non-alphanumeric characters with underscores
    table_name = f"{sanitized_symbol}_data"  # Append "_data" to the sanitized symbol
    try:
        cursor = conn.cursor()
        if not table_exists(cursor, table_name):
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    date DATE NOT NULL PRIMARY KEY,
                    open DECIMAL(15, 5),
                    high DECIMAL(15, 5),
                    low DECIMAL(15, 5),
                    close DECIMAL(15, 5),
                    adj_close DECIMAL(15, 5),
                    volume INT
                )
            """)
            print(f"Table created for {symbol} successfully.")
        else:
            print(f"Table already exists for {symbol}.")
    except Exception as e:
        print(f"Error creating table for {symbol}: {e}")
        return  # Return if an error occurs during table creation

    # Fetch historical data
    data = get_stock_data(symbol)
    if data is None:
        print(f"Failed to download data for {symbol}. Skipping table creation.")
        return

    # Insert data into PostgreSQL
    insert_data(conn, table_name, data)
    # Fetch historical data
    data = get_stock_data(symbol)
    if data is None:
        print(f"Failed to download data for {symbol}. Skipping table creation.")
        return

        

def insert_data(conn, symbol, data):
    """Insert historical data into the PostgreSQL table."""
    try:
        cursor = conn.cursor()
        for index, row in data.iterrows():
            cursor.execute(f"""
                INSERT INTO "{symbol}" (date, open, high, low, adj_close, volume)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date) DO NOTHING
            """, (index.date(), row['Open'], row['High'], row['Low'], row['Close'], row['Volume']))
        print(f"Data inserted for {symbol}.")
    except Exception as e:
        print(f"Error inserting data for {symbol}: {e}")
def validate_symbol(symbol):
    """Validate the symbol."""
    # Implement validation logic here
    # Example: Ensure symbol consists only of letters, numbers, and periods, and is not empty
    if not re.match("^[A-Za-z0-9.]+$", symbol):
        print("Invalid symbol format.")
        return False
    return True
def get_stock_data(symbol):
    """Retrieve historical data from yfinance."""
    if not validate_symbol(symbol):
        return None
    
    try:
        data = yf.download(symbol, start='2019-01-01', end='2024-01-01')
        return data
    except Exception as e:
        print(f"Error retrieving data for {symbol}: {e}")
        return None

def main():
    # Connect to PostgreSQL
    conn = connect_to_postgres()
    if conn is None:
        return

    # Fetch and store data for each symbol
    symbols = ["HDB","RELI","INFY","TCS.NS","ADANIENT.NS"]  
    for symbol in symbols:
        # Create table if not exists
        create_table(conn, symbol)
        
        # Fetch historical data
        data = get_stock_data(symbol)
        if data is not None:
            # Insert data into PostgreSQL
            insert_data(conn, symbol, data)

    # Close PostgreSQL connection
    conn.close()

if __name__ == "__main__":
    main()