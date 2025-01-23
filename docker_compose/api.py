import requests
from datetime import datetime
import time

# API URL
API_URL = "https://api.nobitex.ir/market/udf/history"
FLASK_API_URL = "http://localhost:5000/ingest"  # Flask app endpoint

# List of stock symbols to fetch data for
symbols = ["BTCIRT", "USDTIRT", "ETHIRT", "ETCIRT", "SHIBIRT"]

# Parameters for the API request
resolution = "1"  # 1-minute resolution

def format_timestamp(timestamp):
    """Convert Unix timestamp to local datetime string."""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

try:
    while True:  # Infinite loop for real-time data
        current_time = int(time.time())
        from_time = current_time - 120  # Fetch the last 2 minutes of data

        for symbol in symbols:
            # API request parameters for each stock
            params = {
                "symbol": symbol,
                "resolution": resolution,
                "from": from_time,
                "to": current_time
            }

            # Send GET request to Nobitex API
            response = requests.get(API_URL, params=params)

            if response.status_code == 200:
                data = response.json()
                if data.get("s") == "ok" and data.get("t"):
                    # Extract the latest candle data
                    timestamps = data["t"]
                    open_prices = data["o"]
                    high_prices = data["h"]
                    low_prices = data["l"]
                    close_prices = data["c"]
                    volumes= data['v']
                    # Prepare the latest data point for ingestion
                    latest_index = -1  # Last element
                    payload = {
                        "stock_symbol": symbol,
                        # "timestamp": timestamps,
                        "local_time":format_timestamp(timestamps[latest_index]),
                        "open": open_prices[latest_index],
                        "high": high_prices[latest_index],
                        "low": low_prices[latest_index],
                        "close": close_prices[latest_index],
                        "volume": volumes[latest_index]
                    }

                    # Send the data to the Flask app for ingestion
                    flask_response = requests.post(FLASK_API_URL, json=payload)
                    if flask_response.status_code == 200:
                        flask_response_json = flask_response.json()
                        print(flask_response_json.get("message"),"\n", f"data: {flask_response_json.get('data')}\n\n")
                    else:
                        print(f"Failed to send data to Flask app: {flask_response.status_code}")
                elif data.get("s") == "error":
                    print(f"API Error: {data.get('errmsg')}")
                elif(data.get("s") == "no_data"):
                    print("No new data in the period betwen from and to.")

                else:
                    print("No new data available or API returned an error.")

            else:
                print(f"HTTP Error: {response.status_code}")

        # Wait for the next minute
        time.sleep(60)

except KeyboardInterrupt:
    print("Real-time data fetching stopped by the user.")
except Exception as e:
    print(f"An error occurred: {e}")
