from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, session, flash
import numpy as np
import pandas as pd
import pickle
from flask_cors import CORS
import os
from datetime import datetime
from db import initialize_database, add_user, get_user, verify_user

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = 'your_super_secret_key_here'  # For login sessions

CORS(app)
# Initialize database on startup
initialize_database()

# Ensure static and templates directories exist
os.makedirs("static/images", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Load the trained model and scaler
model = None
scaler = None

try:
    with open("forecast_model2.pkl", "rb") as f:
        model, scaler = pickle.load(f)
    print("✅ Model and scaler loaded successfully")
except Exception as e:
    print(f"❌ Error loading model: {str(e)}")
    print("Make sure forecast_model2.pkl exists in the current directory")

@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')
    return redirect('/emissions')  # Redirect to emissions page if logged in

@app.route('/emissions')
def emissions_page():
    if 'username' not in session:
        return redirect('/login')
    return render_template("emissions.html", username=session['username'])  # Pass username to template

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or scaler is None:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Validate file extension
        if not file.filename.lower().endswith('.csv'):
            return jsonify({"error": "Only CSV files are accepted"}), 400

        # Read and preprocess the data
        df = pd.read_csv(file, skiprows=30)
        
        # Validate required columns
        if len(df.columns) < 2:
            return jsonify({"error": "CSV must contain at least 2 columns (Date and CO2_Damage)"}), 400

        # Rename columns
        df.columns = ['Date', 'CO2_Damage'] + list(df.columns[2:])
        
        # Convert and validate dates
        try:
            df['Date'] = pd.to_datetime(df['Date'])
        except:
            return jsonify({"error": "Invalid date format in CSV"}), 400
            
        df.set_index('Date', inplace=True)
        df = df.sort_index()
        df = df[['CO2_Damage']].dropna()

        # Validate we have enough data
        if len(df) < 10:
            return jsonify({"error": "At least 10 data points required"}), 400

        # Scale the data
        df_scaled = scaler.transform(df.values)
        
        # Create window sequences
        window_size = 10
        windows = [df_scaled[i:i + window_size - 1] 
                  for i in range(len(df_scaled) - window_size + 1)]
        
        X = np.array(windows).reshape(len(windows), window_size - 1, 1)
        
        # Make predictions
        y_pred = model.predict(X)
        y_pred_rescaled = scaler.inverse_transform(y_pred)
        
        # Prepare response data
        dates = df.index[window_size-1:].strftime('%Y-%m-%d').tolist()
        actual_values = df['CO2_Damage'][window_size-1:].tolist()
        
        stats = {
            "mean": float(df['CO2_Damage'].mean()),
            "min": float(df['CO2_Damage'].min()),
            "max": float(df['CO2_Damage'].max()),
            "latest_value": float(df['CO2_Damage'].iloc[-1]),
            "predicted_next": float(y_pred_rescaled[-1][0])
        }
        
        # Future predictions
        future_predictions = predict_future(model, scaler, df)
        last_date = df.index[-1]
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(years=1), 
            periods=12, 
            freq='Y'
        ).strftime('%Y-%m-%d').tolist()
        
        return jsonify({
            "stats": stats,
            "dates": dates,
            "actual": actual_values,
            "predicted": y_pred_rescaled.flatten().tolist(),
            "future_dates": future_dates,
            "future_predictions": future_predictions.flatten().tolist(),
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            "error": "Prediction failed",
            "details": str(e)
        }), 500

def predict_future(model, scaler, df, steps=12):
    last_window = df[-10:].values
    last_window_scaled = scaler.transform(last_window)
    current_window = last_window_scaled[-9:].reshape(-1, 1)
    predictions = []
    
    for _ in range(steps):
        next_pred = model.predict(current_window.reshape(1, 9, 1))[0][0]
        predictions.append(next_pred)
        current_window = np.append(current_window[1:], next_pred).reshape(-1, 1)
    
    return scaler.inverse_transform(np.array(predictions).reshape(-1, 1))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        fullname = request.form.get('fullname')

        # Validate inputs
        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect('/signup')
            
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect('/signup')
            
        if get_user(username):
            flash('Username already exists', 'error')
            return redirect('/signup')

        # Add new user - PASS EMAIL AND FULLNAME HERE
        if add_user(username, password, email, fullname):
            session['username'] = username
            flash('Account created successfully!', 'success')
            return redirect('/emissions')
        else:
            flash('Error creating account', 'error')
            return redirect('/signup')

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if verify_user(username, password):
            session['username'] = username
            return redirect('/emissions')
        else:
            flash("Invalid username or password")
            return redirect('/login')

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully")
    return redirect('/login')





if __name__ == '__main__':
    # Check for required files
    if not os.path.exists("forecast_model2.pkl"):
        print("❌ Error: forecast_model2.pkl not found in root directory")
    
    # Create required directories if they don't exist
    os.makedirs("static/images", exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)