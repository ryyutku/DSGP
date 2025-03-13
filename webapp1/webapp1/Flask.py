from flask import Flask, jsonify
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model  # Sometimes works if keras is separately installed
from tensorflow.keras.losses import MeanSquaredError

custom_objects = {"mse": MeanSquaredError()}

app = Flask(__name__)

# Load your trained LSTM model and scaler
model = load_model("webapp1\webapp1\lstm_model.h5")
scaler = joblib.load("webapp1\webapp1\scaler.pkl")

# Load your original data (adjust the path/format as needed)
df = pd.read_csv("Adjusted Savings Carbon Dioxide Damage.csv", skiprows=30, header=None)
df.columns = ['Date', 'CO2_Damage']
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df = df.sort_index()

@app.route("/forecast", methods=["GET"])
def forecast():
    # Use the last N observations to generate predictions
    time_steps = 10  # Adjust according to your model's sequence length
    recent_data = df[-time_steps:]["CO2_Damage"].values.reshape(-1, 1)
    scaled_recent = scaler.transform(recent_data)
    
    # Forecast next 10 time steps (adjust as needed)
    forecast_steps = 10
    input_seq = scaled_recent.copy()
    future_preds = []
    for _ in range(forecast_steps):
        pred = model.predict(np.array([input_seq]))
        future_preds.append(pred[0][0])
        # Slide the window: remove the first value and append the prediction
        input_seq = np.append(input_seq[1:], [[pred[0][0]]], axis=0)
    
    # Inverse transform predictions to original scale
    future_preds_inv = scaler.inverse_transform(np.array(future_preds).reshape(-1, 1)).flatten()
    
    # Prepare response with both historical and forecast data
    response = {
        "historical_dates": df.index[-50:].strftime("%Y-%m-%d").tolist(),  # Last 50 dates
        "historical_values": df["CO2_Damage"].tail(50).tolist(),
        "forecast_dates": pd.date_range(start=df.index[-1], periods=forecast_steps + 1, freq="Y")[1:].strftime("%Y-%m-%d").tolist(),
        "forecast_values": future_preds_inv.tolist()
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
