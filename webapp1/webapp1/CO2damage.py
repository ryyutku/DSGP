import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Step 1: Load and Preprocess Data
file_path = "C:\\Users\\chana\\OneDrive\\Documents\\IIT\\DSGP\\chanul\\DSGP\\Datasets\\CEIC\\Adjusted Savings Carbon Dioxide Damage.csv"

df = pd.read_csv(file_path, skiprows=30, header=None, names=['Date', 'CO2_Damage'])

# Convert date column to datetime format
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Sort data by date
df = df.sort_index()

# Step 2: Normalize the data
scaler = MinMaxScaler(feature_range=(0, 1))
df_scaled = scaler.fit_transform(df)

# Step 3: Prepare Data for LSTM
def create_sequences(data, time_steps=10):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:i + time_steps])
        y.append(data[i + time_steps])
    return np.array(X), np.array(y)

time_steps = 10
X, y = create_sequences(df_scaled, time_steps)

# Split into training and testing sets (80% training, 20% testing)
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Reshape for LSTM input (samples, time_steps, features)
X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)

# Step 4: Build LSTM Model
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(time_steps, 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')

# Step 5: Train the Model
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_data=(X_test, y_test))

# Step 6: Make Predictions
y_pred = model.predict(X_test)

# Reshape before inverse transforming
y_pred_rescaled = scaler.inverse_transform(y_pred.reshape(-1, 1))
y_test_rescaled = scaler.inverse_transform(y_test.reshape(-1, 1))

# Step 7: Evaluate the Model
mae = mean_absolute_error(y_test_rescaled, y_pred_rescaled)
mse = mean_squared_error(y_test_rescaled, y_pred_rescaled)
rmse = np.sqrt(mse)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")

# Step 8: Plot Actual vs Predicted with Enhanced Styling
plt.figure(figsize=(12, 6))
plt.plot(y_test_rescaled, 'r--', label="Actual CO2 Damage")  # Dotted red line
plt.plot(y_pred_rescaled, 'b-', label="Predicted CO2 Damage")  # Solid blue line
plt.xlabel("Time Steps", fontsize=12)
plt.ylabel("CO2 Damage (USD mn)", fontsize=12)
plt.title("Actual vs Predicted CO2 Damage", fontsize=14, fontweight='bold')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
