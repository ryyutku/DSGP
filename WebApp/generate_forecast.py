import pandas as pd
import numpy as np
from datetime import timedelta
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.offline as pyo
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Load the dataset
data = pd.read_csv('ciec_data.csv')
data = data.drop(columns=['Unnamed: 0'])
data['date'] = pd.to_datetime(data['date'])
data.set_index('date', inplace=True)
data.fillna(method='ffill', inplace=True)

# Define features and target
target_column = 'fuel_consumption'
features = data.drop(columns=[target_column])
target = data[[target_column]]

# Scale features and target
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
scaled_features = scaler_X.fit_transform(features)
scaled_target = scaler_y.fit_transform(target)

# Add noise
noise_factor = 0.05
scaled_features += np.random.normal(0, noise_factor, scaled_features.shape)
scaled_target += np.random.normal(0, noise_factor, scaled_target.shape)

# Create sequences
def create_dataset(features, target, time_steps=30):
    X, y = [], []
    for i in range(time_steps, len(features)):
        X.append(features[i-time_steps:i])
        y.append(target[i])
    return np.array(X), np.array(y)

time_steps = 30
X, y = create_dataset(scaled_features, scaled_target, time_steps)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)

# Build CNN model
model = Sequential()
model.add(Conv1D(64, 3, activation='relu', input_shape=(X.shape[1], X.shape[2])))
model.add(MaxPooling1D(2))
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(1))
model.compile(optimizer=Adam(), loss='mean_squared_error')

# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=1)

# Predict and evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("MSE:", mse, "MAE:", mae, "R2:", r2)

# Plot: actual vs predicted
plt.figure(figsize=(10,6))
plt.plot(scaler_y.inverse_transform(y_test), label="Actual")
plt.plot(scaler_y.inverse_transform(y_pred), label="Predicted")
plt.title("Actual vs Predicted Fuel Consumption")
plt.xlabel("Time")
plt.ylabel("Fuel Consumption")
plt.legend()
plt.savefig('static/actual_vs_predicted.png')
plt.close()

# Plot: loss curve
plt.figure(figsize=(10,6))
plt.plot(history.history['loss'], label="Training Loss")
plt.plot(history.history['val_loss'], label="Validation Loss")
plt.title("Loss Curve")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.savefig('static/loss_curve.png')
plt.close()

# Forecast next 3 months (monthly avg prediction)
recent_data = scaled_features[-time_steps:]
future_predictions = []
num_months = 3

for _ in range(num_months):
    input_seq = recent_data[-time_steps:].reshape(1, time_steps, scaled_features.shape[1])
    prediction = model.predict(input_seq)
    prediction_rescaled = scaler_y.inverse_transform(prediction)[0][0]
    future_predictions.append(prediction_rescaled)
    # Simulate next step
    dummy_input = recent_data[-1]
    recent_data = np.vstack((recent_data[1:], dummy_input))

# Build forecast DataFrame
future_dates = pd.date_range(start=data.index[-1] + timedelta(days=1), periods=num_months, freq='MS')
forecast_df = pd.DataFrame({
    'Month': future_dates.strftime('%B %Y'),
    'Predicted Fuel Consumption': future_predictions
})
forecast_df.to_csv('static/forecast.csv', index=False)

# Plotly Forecast Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=forecast_df['Month'], y=forecast_df['Predicted Fuel Consumption'],
                         mode='lines+markers', name='Forecast'))
fig.update_layout(title='Fuel Demand Forecast (Next 3 Months)',
                  xaxis_title='Month',
                  yaxis_title='Fuel Consumption')
pyo.plot(fig, filename='static/forecast_plot.html', auto_open=False)
