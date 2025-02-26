# Importing required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Load Dataset
data = pd.read_csv('fuel_prices.csv', parse_dates=['Date'], index_col='Date')
print("Dataset Head:")
print(data.head())

# Visualize the Data
plt.figure(figsize=(10, 5))
plt.plot(data, label='Fuel Price')
plt.title('Fuel Price Over Time')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# Split Data into Training and Testing
train_size = int(len(data) * 0.8)
train, test = data[0:train_size], data[train_size:]

# Fit ARIMA Model
model = ARIMA(train, order=(5, 1, 0))
model_fit = model.fit()
print(model_fit.summary())

# Forecast
forecast = model_fit.forecast(steps=len(test))
forecast = pd.Series(forecast, index=test.index)

# Visualize Forecast vs Actual
plt.figure(figsize=(10, 5))
plt.plot(train, label='Training Data')
plt.plot(test, label='Actual Prices')
plt.plot(forecast, label='Predicted Prices', color='red')
plt.title('Fuel Price Prediction')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

# Evaluation Metrics
mse = mean_squared_error(test, forecast)
mae = mean_absolute_error(test, forecast)
rmse = np.sqrt(mse)
print(f'Mean Absolute Error (MAE): {mae}')
print(f'Mean Squared Error (MSE): {mse}')
print(f'Root Mean Squared Error (RMSE): {rmse}')
