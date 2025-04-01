import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

base_url = "https://ceypetco.gov.lk/historical-prices/page/{}/"
headers = {"User-Agent": "Mozilla/5.0"}
all_data = []

for page in range(1, 18):  # For the available 17 pages
    url = base_url.format(page)
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    for row in soup.select("table tbody tr"):
        cols = row.find_all("td")
        if len(cols) >= 5:
            date_str = cols[0].text.strip()
            petrol_str = cols[1].text.strip().replace(",", "")
            diesel_str = cols[4].text.strip().replace(",", "")

            try:
                date = datetime.strptime(date_str, "%d.%m.%Y")
                petrol = float(petrol_str)
                diesel = float(diesel_str)
                all_data.append([date, petrol, diesel])
            except Exception as e:
                continue  # Skipping if date or prices are invalid

# Create DataFrame
df = pd.DataFrame(all_data, columns=["Date", "Petrol_Price", "Diesel_Price"])

# Remove duplicates (if any) by date
df = df.drop_duplicates(subset="Date").sort_values("Date").reset_index(drop=True)

# Save to CSV
df.to_csv("/Users/yehana2002/Projects/DSGP/datasets/processed/full_sri_lanka_fuel_prices.csv", index=False)
print("Final cleaned dataset saved to full_sri_lanka_fuel_prices.csv")
