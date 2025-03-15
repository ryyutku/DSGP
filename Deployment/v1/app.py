from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import plotly
import plotly.graph_objs as go
import json


app = Flask(__name__)


# Loading the trained model
with open('fuel_demand.pkl','rb') as f:
    model = pickle.load(f)

# Load the scalers (assuming you have saved them)
with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open ('fuel_scaler.pkl','rb') as f:
    fuel_scaler = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.rounte('/predict', methods=['POST'])
def predict():
    # Get the data from the POST request
    data = request.json['data']

    # convert data into a dataframe
    future_df = pd.DataFrame(data)

    # Prepare future data (Scaling the features)
    future_numerical_cols = future_df.select_dtypes(include=['float64','int64']).columns
    future_numerical_cols = future_numerical_cols.drop('fuel_consumption', errors='ignore')

    # Applying the same scaling transfomation as the training data
    future_df[future_numerical_cols] = scaler.transform(future_df[future_numerical_cols])

    # Make predictions on the future dataset
    future_predictions = model.predict(future_df)

    # Inverse transform the predictions to get real-world fuel consumption values
    future_predictions = fuel_scaler.inverse_transform(future_predictions.reshape(-1,1))

    # Add predictions to the future dataframe
    future_df['predicted_fuel_demand'] = future_predictions

    # Create a Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=future_df['date'],
        y=future_df['predicted_fuel_demand'],
        model='lines+makers',
        name='Forecasted Fuel Demand',
        line=dict(color='green',dash='dash')        
    ))

    # Layout settings
    fig.update_layout(
        title='Forecasted Fuel Demand',
        xaxis_title = 'Date',
        yaxis_title = 'Fuel Demand',
        showlegend = True
    )

    # Convert the figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return jsonify(graphJSON)

if __name__ == '__main__':
    app.run(debug=True)