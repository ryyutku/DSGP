import requests
import pandas as pd
from datetime import datetime, timedelta
import time

#  API KEYS (Replace with your actual keys)
ALPHA_VANTAGE_API_KEY = "demo"
WEATHER_API_KEY = "c93fef59ffa5098a48d7392901815f3a"

#  API ENDPOINTS
OIL_PRICE_API = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=CL=F&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}"
WEATHER_API = f"https://api.openweathermap.org/data/2.5/weather?q=Colombo&appid={WEATHER_API_KEY}&units=metric"

#  Function to fetch real-time oil price from Alpha Vantage
def fetch_oil_price():
    try:
        response = requests.get(OIL_PRICE_API)
        data = response.json()
        if "Time Series (5min)" in data:
            latest_time = list(data["Time Series (5min)"].keys())[0]
            return float(data["Time Series (5min)"][latest_time]["1. open"])
        else:
            print("Alpha Vantage API limit exceeded or invalid response.")
            return None
    except Exception as e:
        print(f"Error fetching oil price: {e}")
        return None

#  Function to fetch real-time weather data from OpenWeather
def fetch_weather():
    try:
        response = requests.get(WEATHER_API)
        data = response.json()
        if "main" in data:
            return data["main"]["temp"]  # Temperature in Celsius
        else:
            print(" Invalid weather API response.")
            return None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

#  Function to collect and store data
def collect_data(days=30):
    dates = [datetime.today() - timedelta(days=i) for i in range(days)]
    oil_prices = []
    temperatures = []

    for i in range(days):
        oil_price = fetch_oil_price()
        temperature = fetch_weather()

        if oil_price is not None and temperature is not None:
            oil_prices.append(oil_price)
            temperatures.append(temperature)
        else:
            oil_prices.append(None)
            temperatures.append(None)

        time.sleep(12)  # Avoid hitting API rate limits

    df = pd.DataFrame({"date": dates, "oil_price": oil_prices, "temperature": temperatures})
    df.to_csv("oil_demand_data.csv", index=False)
    print(" Dataset saved as oil_demand_data.csv")
    return df

#  Run data collection
if __name__ == "__main__":
    df = collect_data()
    print(df.head())  # Display the first few rows
