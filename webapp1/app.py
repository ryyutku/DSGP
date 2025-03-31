from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
import pickle
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Load the trained model and scaler
try:
    with open("forecast_model2.pkl", "rb") as f:
        model, scaler = pickle.load(f)
except:
    print("Error loading model. Make sure forecast_model.pkl exists in the current directory.")

@app.route('/')
def index():
    return render_template("emissions.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Read and preprocess the data
        df = pd.read_csv(file, skiprows=30)
        
        # Rename columns for consistency with training
        if len(df.columns) >= 2:
            df.columns = ['Date', 'CO2_Damage'] + list(df.columns[2:])
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # Sort data by date
            df = df.sort_index()
            
            # Keep only the CO2_Damage column
            df = df[['CO2_Damage']]
        else:
            return jsonify({"error": "Invalid file format. Expected columns for Date and CO2_Damage."}), 400

        # Scale the data
        df_scaled = scaler.transform(df.values)
        
        # Create window sequences for prediction (like in training)
        window_size = 10
        windows = []
        for i in range(len(df_scaled) - window_size + 1):
            windows.append(df_scaled[i:i + window_size - 1])
        
        if not windows:
            return jsonify({"error": "Not enough data points for prediction"}), 400
            
        X = np.array(windows)
        X = X.reshape(X.shape[0], X.shape[1], 1)
        
        # Make predictions
        y_pred = model.predict(X)
        y_pred_rescaled = scaler.inverse_transform(y_pred)
        
        # Create dates for x-axis
        dates = df.index[window_size-1:].strftime('%Y-%m-%d').tolist()
        
        # Get actual values for comparison
        actual_values = df['CO2_Damage'][window_size-1:].tolist()
        
        # Calculate basic statistics
        stats = {
            "mean": float(np.mean(actual_values)),
            "min": float(np.min(actual_values)),
            "max": float(np.max(actual_values)),
            "latest_value": float(actual_values[-1]),
            "predicted_next": float(y_pred_rescaled[-1][0])
        }
        
        # Prepare future predictions (next 12 periods)
        future_predictions = predict_future(model, scaler, df, future_steps=12)
        
        # Create future dates (assuming annual data like in your training script)
        last_date = df.index[-1]
        future_dates = pd.date_range(start=last_date + pd.DateOffset(years=1), periods=12, freq='Y')
        future_dates = future_dates.strftime('%Y-%m-%d').tolist()
        
        return jsonify({
            "dates": dates,
            "actual": actual_values,
            "predicted": y_pred_rescaled.flatten().tolist(),
            "future_dates": future_dates,
            "future_predictions": future_predictions.flatten().tolist(),
            "stats": stats
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def predict_future(model, scaler, df, future_steps=12):
    last_window = df[-10:].values
    last_window_scaled = scaler.transform(last_window)
    future_predictions = []

    current_window = last_window_scaled[-9:].reshape(-1, 1)
    
    for _ in range(future_steps):
        # Prepare the input sequence (the last 9 known values)
        input_seq = current_window.reshape(1, 9, 1)
        # Predict the next value
        next_pred = model.predict(input_seq)[0][0]
        future_predictions.append(next_pred)
        # Update the window by removing the first element and adding the prediction
        current_window = np.append(current_window[1:], next_pred).reshape(-1, 1)

    future_predictions_rescaled = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
    return future_predictions_rescaled

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)