from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Initialize the Flask app
app = Flask(__name__)

# Load the trained model
model_arima = joblib.load('arima_model.pkl')

# Example function to forecast and plot the results
def forecast_and_plot(data):
    # Preprocess the input data (if necessary)
    # In this case, we assume you're passing the necessary time series data
    
    # Perform prediction (replace with actual prediction logic)
    forecast = model_arima.predict(start=0, end=10)  # Example prediction range
    
    # Create a plot
    fig, ax = plt.subplots()
    ax.plot(forecast, label="Forecast")
    ax.set_title("Forecast Plot")
    ax.set_xlabel("Time")
    ax.set_ylabel("Demand")
    ax.legend()

    # Save the plot as an image to display in the browser
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return base64.b64encode(output.getvalue()).decode('utf8')

@app.route('/')
def index():
    # Home route rendering the index page
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Get data from the form (assuming you're passing some parameters for prediction)
    # For this example, we are just forecasting for a specific period
    data = request.form['input_data']  # You can collect specific data from the user

    # Get forecast plot image
    plot_url = forecast_and_plot(data)
    
    # Return the plot image URL to be displayed on the website
    return jsonify({'plot_url': plot_url})

if __name__ == '__main__':
    app.run(debug=True)
