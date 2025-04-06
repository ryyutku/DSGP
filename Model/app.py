import matplotlib
matplotlib.use('Agg')  # Not used now but kept for safety in environments

import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from pmdarima import auto_arima
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
from flask import Flask, render_template
import plotly.graph_objs as go
from plotly.offline import plot

# Load .env
load_dotenv()

# Flask App
app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)

# Load Data
try:
    inventory_data = pd.read_csv("cleaned_inventory_dataset.csv")
except Exception as e:
    logging.error(f"Error loading dataset: {e}")
    exit(1)

# Data Cleanup
required_columns = {'Date', 'Current_Stock', 'Fuel_Type', 'Reorder_Level'}
if not required_columns.issubset(inventory_data.columns):
    raise ValueError(f"Dataset must contain: {', '.join(required_columns)}")

inventory_data['Date'] = pd.to_datetime(inventory_data['Date'])
inventory_data.set_index('Date', inplace=True)
inventory_data.sort_index(inplace=True)
inventory_data['Current_Stock'] = pd.to_numeric(inventory_data['Current_Stock'], errors='coerce')
inventory_data['Reorder_Level'] = pd.to_numeric(inventory_data['Reorder_Level'], errors='coerce')
inventory_data.ffill(inplace=True)

# ARIMA Model
def train_ARIMA(group):
    try:
        model = auto_arima(group['Current_Stock'], seasonal=False, trace=False,
                           error_action='ignore', suppress_warnings=True)
        model_fit = model.fit(group['Current_Stock'])
        logging.info(f"ARIMA model trained for {group['Fuel_Type'].iloc[0]}")
        return model_fit
    except Exception as e:
        logging.error(f"ARIMA training failed for {group['Fuel_Type'].iloc[0]}: {e}")
        return None

def forecast_inventory_ARIMA(model, periods):
    if model:
        forecast = model.predict(n_periods=periods)
        logging.info(f"Forecasted values: {forecast}")
        return forecast
    else:
        logging.error("Model is None, cannot forecast")
        return None

# Email Alerts
def send_alert_email(fuel_type):
    try:
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        recipient_email = os.getenv("RECIPIENT_EMAIL")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT"))

        subject = f"Low Stock Alert for {fuel_type}"
        body = f"⚠️ Warning: {fuel_type} stock is below reorder level. Please restock."

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        logging.info(f"Email alert sent for {fuel_type}")
    except Exception as e:
        logging.error(f"Email send failed: {e}")

# Plotly Graph
def plot_stock_levels_plotly(group, forecast):
    fuel_type = group['Fuel_Type'].iloc[0]

    traces = [
        go.Scatter(x=group.index, y=group['Current_Stock'], mode='lines', name='Current Stock', line=dict(color='blue')),
        go.Scatter(x=group.index, y=group['Reorder_Level'], mode='lines', name='Reorder Level', line=dict(color='red', dash='dash'))
    ]

    # Append forecast to future dates
    if forecast is not None:
        last_date = group.index[-1]
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=len(forecast), freq='D')
        traces.append(go.Scatter(x=future_dates, y=forecast, mode='lines', name='Forecast', line=dict(color='green', dash='dot')))

    layout = go.Layout(
        title=f'Stock vs Reorder Level for {fuel_type}',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Stock Level'),
        legend=dict(x=0, y=1),
        template='plotly_white'
    )

    fig = go.Figure(data=traces, layout=layout)
    return plot(fig, output_type='div', include_plotlyjs=False)

# Route
@app.route('/')
def index():
    plots = {}
    for fuel_type, group in inventory_data.groupby('Fuel_Type'):
        arima_model = train_ARIMA(group)
        forecast = forecast_inventory_ARIMA(arima_model, periods=7)
        logging.info(f"Generated forecast for {fuel_type}: {forecast}")

        plot_div = plot_stock_levels_plotly(group, forecast)
        low_stock = group['Current_Stock'].iloc[-1] < group['Reorder_Level'].iloc[-1]

        if low_stock:
            send_alert_email(fuel_type)

        plots[fuel_type] = {
            'plot_div': plot_div,
            'low_stock': low_stock,
            'forecast': forecast.tolist() if forecast is not None else []
        }

    return render_template('index.html', plots=plots)

if __name__ == "__main__":
    app.run(debug=True)
