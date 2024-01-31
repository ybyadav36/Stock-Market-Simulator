import scrapy
from pymongo import MongoClient

# Connect to your MongoDB instance
client = MongoClient('mongodb://localhost:27017/')

# Select the database and collection where you want to store the data
db = client['my-mongodb-container']
collection = db['NSE_Data']

class NseSpider(scrapy.Spider):
    name = 'nse'
    allowed_domains = ['nseindia.com']
    start_urls = ['https://www.nseindia.com/products/content/equities/equities/eq_security.htm']

    # Initialize the counter variable
    inserted_records = 0

    def parse(self, response):
        # Scrape the list of equity securities
        securities = response.css('table.dataTable tbody tr')

        for security in securities:
            # Extract the security name and symbol
            name = security.css('td:nth-child(1) a::text').get()
            symbol = security.css('td:nth-child(2)::text').get()

            # Create a dictionary with the security data
            security_data = {
                'name': name,
                'symbol': symbol
            }

            # Store the security data in the MongoDB collection
            collection.insert_one(security_data)
            self.inserted_records += 1

            # Follow the link to the security's detail page
            yield response.follow(security.css('td:nth-child(1) a::attr(href)').get(), self.parse_security)

    def parse_security(self, response):
        # Extract the security's detailed information
        name = response.css('h1::text').get()
        symbol = response.css('span.symbol::text').get()
        market_capitalization = response.css('span.marketCapitalization::text').get()
        price_earnings_ratio = response.css('span.peRatio::text').get()
        price_to_book_value = response.css('span.priceToBookValue::text').get()
        dividend_yield = response.css('span.dividendYield::text').get()

        # Create a dictionary with the security's detailed information
        security_data = {
            'name': name,
            'symbol': symbol,
            'market_capitalization': market_capitalization,
            'price_earnings_ratio': price_earnings_ratio,
            'price_to_book_value': price_to_book_value,
            'dividend_yield': dividend_yield
        }

        # Store the security's detailed information in the MongoDB collection
        collection.insert_one(security_data)
        self.inserted_records += 1

        # Print the number of records inserted
        print(f"{self.inserted_records} records inserted")