import requests
from bs4 import BeautifulSoup
import csv
import datetime
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from retrying import retry

# Retry decorator with exponential backoff
@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
def fetch_url(url, headers=None, proxies=None):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    response = session.get(url, headers=headers, proxies=proxies)
    response.raise_for_status()
    return response

# Make a request to the NSE India website with retry mechanism and proxy configuration
url = "https://www.google.com/finance/markets/most-active?hl=en"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
proxies = {
    "http": "http://your_proxy_address",
    "https": "https://your_proxy_address",
}

try:
    response = fetch_url(url, headers=headers, proxies=proxies)
    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table containing the data
    table = soup.find("table", {"class": "WideTable", "summary": "Market Watch - Indices"})

    # Extract the header row and the data rows
    header_row = table.thead.tr
    data_rows = table.tbody.find_all("tr")

    # Extract the header columns
    header_columns = [th.text.strip() for th in header_row.find_all("th")]

    # Initialize an empty list to store the data
    data = []

    # Iterate over the data rows and extract the data columns
    for row in data_rows:
        columns = row.find_all("td")
        data.append([td.text.strip() for td in columns])

    # Remove the first column (which contains the index names)
    data = [row[1:] for row in data]

    # Convert the date strings to datetime objects
    data = [list(map(datetime.datetime.strptime, row, ["%d-%b-%Y %H:%M:%S"] * len(row))) for row in data]

    # Write the data to a CSV file
    with open("nse_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header_columns)
        writer.writerows(data)
        
    print("Data successfully scraped and saved to 'nse_data.csv'.")

except Exception as e:
    print("Failed to retrieve the webpage:", e)