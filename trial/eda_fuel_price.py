# Importing Libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np

# Generating dummy data 
dates = pd.date_range(start="2023-01-01", periods=100)
prices = np.random.normal(loc=350, scale=15, size=len(dates))
data = pd.DataFrame({'Date': dates, 'Fuel_Price': prices})

# Quick Summary
print("Dataset Overview:")
print(data.head())
print(data.describe())

# Convert Date column to datetime format
data['Date'] = pd.to_datetime(data['Date'])

# Time Series Plot
plt.figure(figsize=(10, 6))
plt.plot(data['Date'], data['Fuel_Price'], label='Fuel Price', color='blue')
plt.title('Fuel Price Over Time')
plt.xlabel('Date')
plt.ylabel('Price (LKR)')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()

# Correlation Heatmap
correlation = data.corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap')
plt.show()

# Distribution Plot
sns.histplot(data['Fuel_Price'], bins=20, color='purple')
plt.title('Fuel Price Distribution')
plt.xlabel('Fuel Price (LKR)')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

# Check for Missing Values
print("\nMissing Values:")
print(data.isnull().sum())

# Filling Missing Values (if any)
data['Fuel_Price'].interpolate(method='linear', inplace=True)

# Feature Engineering
data['Day'] = data['Date'].dt.day
data['Week'] = data['Date'].dt.isocalendar().week
data['Month'] = data['Date'].dt.month
data['Quarter'] = data['Date'].dt.quarter
data['Year'] = data['Date'].dt.year

# Lag Features
data['Lag_1'] = data['Fuel_Price'].shift(1)
data['Lag_7'] = data['Fuel_Price'].shift(7)
data['Lag_30'] = data['Fuel_Price'].shift(30)

# Rolling Averages
data['Rolling_Mean_7'] = data['Fuel_Price'].rolling(window=7).mean()
data['Rolling_Mean_30'] = data['Fuel_Price'].rolling(window=30).mean()

# Drop rows with NaN values from Lag and Rolling features
data.dropna(inplace=True)

# Verify the DataFrame
print("\nData after Feature Engineering:")
print(data.head())

# Correlation Heatmap with new features
correlation = data.corr()
plt.figure(figsize=(10, 8))
sns.heatmap(correlation, annot=True, cmap='coolwarm')
plt.title('Correlation Heatmap with Feature Engineering')
plt.show()

