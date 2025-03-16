from flask import Flask, request, jsonify, render_template  # Add render_template here
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
import plotly
import plotly.graph_objs as go
import json
from datetime import datetime

app = Flask(__name__)

# Load the trained model
with open('fuel_demand.pkl', 'rb') as f:
    model = pickle.load(f)

# Load the scalers
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('fuel_scaler.pkl', 'rb') as f:
    fuel_scaler = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')  # This will now work

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        # Read the file into a DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            return jsonify({"error": "Unsupported file format. Please upload a CSV or Excel file."}), 400

        # Ensure the required columns are present
        required_columns = ['fuel_consumption', 'petroleum_imports_crudeOil',
       'Taxes_on_Customs_and_Other_Import Duties',
       'Foreign Direct Investments', 'GDP Goods and Services',
       'New Vehicle Registrations', 'Vehicle Sales', 'Vehicle Sales Asia',
       'No.of Vessels Colombo', 'Imports of Refined Products',
       'Tax income profits_gains', 'Tax Goods & Services',
       'Tax Road Transport', 'GDP FCE Households', 'Diesel User Price',
       'Petrol User Price', 'Consumption_Oil', 'Sales 90 Octane',
       'Sales 95 Octane', 'Sales Auto Diesel', 'year', 'month', 'day',
       'weekday', 'quarter']

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({"error": f"Missing required columns: {missing_columns}"}), 400

        # Save the dates for plotting
        dates = df['date']

        # Preprocess the data
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['weekday'] = df['date'].dt.weekday
        df['quarter'] = df['date'].dt.quarter

        # Drop the date column
        df.drop('date', axis=1, inplace=True)

        # Scale the features
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        df[numerical_cols] = scaler.transform(df[numerical_cols])

        # Make predictions
        predictions = model.predict(df)
        predictions = fuel_scaler.inverse_transform(predictions.reshape(-1, 1))

        # Add predictions and dates to a DataFrame
        results_df = pd.DataFrame({
            'date': dates,
            'predicted_fuel_demand': predictions.flatten()
        })

        # Create a Plotly figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=results_df['date'], y=results_df['predicted_fuel_demand'],
            mode='lines+markers',
            name='Forecasted Fuel Demand',
            line=dict(color='green', dash='dash')
        ))

        # Layout settings
        fig.update_layout(
            title='Forecasted Fuel Demand',
            xaxis_title='Date',
            yaxis_title='Fuel Demand',
            showlegend=True
        )

        # Convert the figure to JSON
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return jsonify(graphJSON)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)