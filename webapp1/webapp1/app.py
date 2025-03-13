from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from werkzeug.utils import secure_filename
import os

# Load the model
model = tf.keras.models.load_model("co2_emission_lstm_model.h5")

# Initialize scaler (this should be the same scaler you used during training)
scaler = MinMaxScaler()

# Flask app setup
app = Flask(__name__)

# Set up folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# API endpoint to upload CSV and get predictions
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the CSV file
        df = pd.read_csv(file_path, header=None)
        df.columns = ["Date", "CO2_Emissions"]

        # Convert Date column to datetime format
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Remove rows with invalid/missing dates
        df.dropna(subset=["Date"], inplace=True)

        # Set Date as the index
        df.set_index("Date", inplace=True)
        df = df.sort_index()

        # Normalize the data
        data_scaled = scaler.fit_transform(df[["CO2_Emissions"]])

        # Create sequences (same as during training)
        time_steps = 10
        X = []
        for i in range(len(data_scaled) - time_steps):
            X.append(data_scaled[i : i + time_steps])

        X = np.array(X)

        # Make predictions
        predictions = model.predict(X)
        predictions = scaler.inverse_transform(predictions)  # Convert back to original scale

        # Return predictions as JSON response
        return jsonify({"predictions": predictions.tolist()})

    else:
        return jsonify({"error": "Invalid file format. Only CSV files are allowed."}), 400

if __name__ == '__main__':
    app.run(debug=True)
