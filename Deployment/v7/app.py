# from flask import Flask, request, render_template
# import pandas as pd
# import pickle
# import numpy as np
# import plotly.express as px
# import plotly.graph_objects as go

# app = Flask(__name__)

# # Load the trained model and scalers
# with open('rf_model.pkl', 'rb') as model_file:
#     model = pickle.load(model_file)

# with open('feature_scaler.pkl', 'rb') as fscaler_file:
#     feature_scaler = pickle.load(fscaler_file)

# with open('target_scaler.pkl', 'rb') as tscaler_file:
#     target_scaler = pickle.load(tscaler_file)

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     if 'file' not in request.files:
#         return "No file uploaded!", 400

#     file = request.files['file']

#     if file.filename == '':
#         return "No selected file!", 400

#     # Read the uploaded CSV file
#     df = pd.read_csv(file)

#     # Convert date column to datetime if present
#     if 'date' in df.columns:
#         df['date'] = pd.to_datetime(df['date'])
#         df['year'] = df['date'].dt.year
#         df['month'] = df['date'].dt.month
#         df['day'] = df['date'].dt.day
#         df['weekday'] = df['date'].dt.weekday
#         df['quarter'] = df['date'].dt.quarter
#         df.drop(columns=['date'], inplace=True)

#     # Drop columns that were removed during training
#     drop_cols = ['Household_income', 'Fuel_other_manufacture', 'Tax on Export', 'Colombo port calls',
#                  'Port Stay Duration', 'GDP: Gross National Income', 'Government Debt']

#     df.drop(columns=[col for col in drop_cols if col in df.columns], inplace=True)

#     # Apply feature scaling
#     numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
#     df[numerical_cols] = feature_scaler.transform(df[numerical_cols])

#     # Predict fuel demand
#     predictions = model.predict(df)

#     # Inverse transform predictions
#     predicted_values = target_scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()

#     # Add predictions to the DataFrame
#     df['Predicted Fuel Demand'] = predicted_values

#     # Create Plotly graph
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(y=df['Predicted Fuel Demand'], mode='lines+markers', name='Predicted Fuel Demand'))
#     fig.update_layout(title='Predicted Fuel Demand', xaxis_title='Time', yaxis_title='Fuel Demand')

#     # Convert graph to HTML
#     graph_html = fig.to_html(full_html=False)

#     return render_template('result.html', table=df.to_html(), graph_html=graph_html)

# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, request, render_template, flash
import pandas as pd
import pickle
import numpy as np
import plotly.graph_objects as go

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flashing messages

# Load the trained model and scalers
with open('rf_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('feature_scaler.pkl', 'rb') as fscaler_file:
    feature_scaler = pickle.load(fscaler_file)

with open('target_scaler.pkl', 'rb') as tscaler_file:
    target_scaler = pickle.load(tscaler_file)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        flash("No file uploaded!", "error")
        return render_template('index.html')

    file = request.files['file']
    if file.filename == '':
        flash("No selected file!", "error")
        return render_template('index.html')

    # Read the uploaded CSV file
    df = pd.read_csv(file)

    # Convert 'date' column to datetime if present
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        df['weekday'] = df['date'].dt.weekday
        df['quarter'] = df['date'].dt.quarter
        df.set_index('date', inplace=True)  # Keep date for plotting

    else:
        flash("Error: The CSV must have a 'date' column.", "error")
        return render_template('index.html')

    # Drop unnecessary columns
    drop_cols = ['Household_income', 'Fuel_other_manufacture', 'Tax on Export', 'Colombo port calls',
                 'Port Stay Duration', 'GDP: Gross National Income', 'Government Debt']

    df.drop(columns=[col for col in drop_cols if col in df.columns], inplace=True)

    # Apply feature scaling (drop non-numeric columns first)
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[numerical_cols] = feature_scaler.transform(df[numerical_cols])

    # Predict fuel demand
    predictions = model.predict(df)

    # Inverse transform predictions
    predicted_values = target_scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()

    # Add predictions to the DataFrame
    df['Predicted Fuel Demand'] = predicted_values

    # Create Plotly graph with correct time labels
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,  # Use actual time periods instead of index numbers
        y=df['Predicted Fuel Demand'],
        mode='lines+markers',
        name='Predicted Fuel Demand'
    ))

    fig.update_layout(
        title='Predicted Fuel Demand',
        xaxis_title='Time Periods',
        yaxis_title='Fuel Demand'
    )

    # Convert graph to HTML
    graph_html = fig.to_html(full_html=False)

    return render_template('result.html', table=df.to_html(), graph_html=graph_html)

if __name__ == '__main__':
    app.run(debug=True)
