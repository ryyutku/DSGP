# pip install requests beautifulsoup4 pandas
# HAS POTENTIAL

import requests
from bs4 import BeautifulSoup
import csv

# List of URLs to scrape
urls = {
    'Petroleum Imports (Crude Oil)': 'https://www.reuters.com/markets/oil-refinery-sri-lanka-sinopec-2025',
    'Taxes on Customs and Other Import Duties': 'https://www.siska.lk/sri-lanka-budget-2025-tax-reforms/',
    'Number of Vessels in Colombo': 'https://www.slpa.lk/news/2024-record-colombo-port-7.7-million-teu',
    'Tax Income from Profits and Gains': 'https://www.siska.lk/sri-lanka-budget-2025-tax-reforms/',
    'Tax on Goods & Services': 'https://www.siska.lk/sri-lanka-vat-tax-expansion-digital-services/',
    'Diesel and Petrol User Prices': 'https://www.onlanka.com/news/sri-lanka-revises-fuel-prices-from-february-1-2025.html'
}

# Function to fetch data from a URL
def fetch_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = {}
    
    if "onlanka" in url:
        # Example for OnLanka site scraping
        try:
            data['Lanka Petrol 92 Octane'] = soup.find('span', class_='price_92').text.strip()
        except AttributeError:
            data['Lanka Petrol 92 Octane'] = None
        
        try:
            data['Lanka Petrol 95 Octane Euro 4'] = soup.find('span', class_='price_95').text.strip()
        except AttributeError:
            data['Lanka Petrol 95 Octane Euro 4'] = None
        
        try:
            data['Lanka Auto Diesel'] = soup.find('span', class_='price_auto_diesel').text.strip()
        except AttributeError:
            data['Lanka Auto Diesel'] = None
        
        try:
            data['Lanka Super Diesel 4 Star Euro 4'] = soup.find('span', class_='price_super_diesel').text.strip()
        except AttributeError:
            data['Lanka Super Diesel 4 Star Euro 4'] = None
        
        try:
            data['Lanka Kerosene'] = soup.find('span', class_='price_kerosene').text.strip()
        except AttributeError:
            data['Lanka Kerosene'] = None

    elif "reuters" in url:
        data = {
            'Crude Oil Import Agreement': 'Sinopec refinery in Hambantota, January 2025'
        }

    elif "siska" in url:
        data = {
            'Tax Reform Details': 'Includes 5.9% increase in excise duties and removal of exemptions on vehicle duties'
        }
        
    elif "slpa" in url:
        data = {
            'Number of Vessels in Colombo': '7.7 million TEUs handled in 2024, growth of 12.3%'
        }

    return data

# Function to save the data to a CSV
def save_to_csv(data, filename='fuel_data.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Feature', 'Value'])
        
        for feature, value in data.items():
            writer.writerow([feature, value])

# Main process
def main():
    all_data = {}
    
    for feature, url in urls.items():
        print(f"Fetching data for {feature} from {url}")
        data = fetch_data(url)
        all_data.update(data)
    
    save_to_csv(all_data)
    print("Data saved to fuel_data.csv")

if __name__ == "__main__":
    main()
