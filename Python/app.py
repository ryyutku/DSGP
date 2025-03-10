from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
from sklearn.preprocessing import StandardScaler

# Initialize Flask app
app = Flask(__name__)

# Load the trained model and scaler
model = pickle.load(open("fuel_demand_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
fuel_scaler = pickle.load(open("fuel_scaler.pkl", "rb"))

# Define API endpoint for predictions
@app.route('/predict', methods=['POST'])
def predict_demand():
    data = request.json  # Get input from request
    df_input = pd.DataFrame(data)  # Convert input to DataFrame

    # Apply feature engineering
    df_input['year'] = pd.to_datetime(df_input['date']).dt.year
    df_input['month'] = pd.to_datetime(df_input['date']).dt.month
    df_input['day'] = pd.to_datetime(df_input['date']).dt.day
    df_input['weekday'] = pd.to_datetime(df_input['date']).dt.weekday
    df_input['quarter'] = pd.to_datetime(df_input['date']).dt.quarter

    df_input.drop('date', axis=1, inplace=True)

    # Standardize input features
    numerical_cols = df_input.columns
    df_input[numerical_cols] = scaler.transform(df_input[numerical_cols])

    # Predict fuel demand
    prediction = model.predict(df_input)
    prediction_original_scale = fuel_scaler.inverse_transform(prediction.reshape(-1, 1)).flatten()

    return jsonify({"predicted_fuel_demand": prediction_original_scale.tolist()})

# Define route to render forecast visualization
@app.route('/forecast', methods=['GET'])
def render_forecast():
    # Simulated historical and predicted data (Replace with actual DB retrieval)
    dates = pd.date_range(start="2025-01-01", periods=30, freq="D")
    actual_values = np.random.randint(500, 1500, size=30)
    predicted_values = actual_values + np.random.randint(-100, 100, size=30)

    # Create interactive Plotly visualization
    trace_actual = go.Scatter(x=dates, y=actual_values, mode='lines+markers', name='Actual Demand', line=dict(color='blue'))
    trace_predicted = go.Scatter(x=dates, y=predicted_values, mode='lines+markers', name='Predicted Demand', line=dict(color='red', dash='dash'))
    
    layout = go.Layout(title='Actual vs Predicted Fuel Demand', xaxis=dict(title='Date'), yaxis=dict(title='Fuel Demand'))
    fig = go.Figure(data=[trace_actual, trace_predicted], layout=layout)
    
    graph_html = pio.to_html(fig, full_html=False)
    
    return render_template('forecast.html', plot=graph_html)

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
