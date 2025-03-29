from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the trained forecasting model
model_data = joblib.load("forecast_model.pkl")

# Check if the loaded data is a tuple and extract the model
if isinstance(model_data, tuple):
    model = model_data[0]  # Assuming the model is the first element in the tuple
else:
    model = model_data  # If it's not a tuple, assume it's the model itself

def generate_forecast_chart(predictions):
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(predictions) + 1), predictions, marker='o', linestyle='-')
    plt.xlabel("Time")
    plt.ylabel("Predicted Value")
    plt.title("Forecasting Predictions")
    
    # Convert plot to base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return plot_url

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        df = pd.read_csv(file, skiprows=30)  # Adjust 'skiprows' if necessary
        df = df.select_dtypes(include=[np.number])  # Keep only numeric columns

        if df.empty:
            return jsonify({"error": "No valid numerical data found in CSV"}), 400

        input_data = df.values  # Convert dataframe to numpy array
        predictions = model.predict(input_data).tolist()

        # Debugging: Print predictions to console
        print("Predictions:", predictions)

        return jsonify({"predictions": predictions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)