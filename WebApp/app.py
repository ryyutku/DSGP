# from flask import Flask, render_template, request
# import os

# app = Flask(__name__)

# # Folder to store uploaded files
# UPLOAD_FOLDER = 'uploads/'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Ensure the upload folder exists
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# # Route for home page
# @app.route('/')
# def home():
#     return render_template('index.html')

# # Route for demand forecasting page
# @app.route('/demand_forecasting')
# def demand_forecasting():
#     return render_template('demand_forecasting.html')

# # Route to handle PDF file upload
# @app.route('/upload_pdf', methods=['POST'])
# def upload_pdf():
#     if 'pdf_file' not in request.files:
#         return 'No file part', 400
#     file = request.files['pdf_file']
#     if file.filename == '':
#         return 'No selected file', 400
#     # Save the file to the upload folder
#     file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
#     return 'PDF uploaded successfully!', 200

# # Route to handle CSV file upload
# @app.route('/upload_csv', methods=['POST'])
# def upload_csv():
#     if 'csv_file' not in request.files:
#         return 'No file part', 400
#     file = request.files['csv_file']
#     if file.filename == '':
#         return 'No selected file', 400
#     # Save the file to the upload folder
#     file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
#     return 'CSV uploaded successfully!', 200

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import subprocess
from db import add_user, verify_user, get_user  # Import database functions

app = Flask(__name__)

# Routes for Home and Demand Forecasting
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demand_forecasting')
def demand_forecasting():
    return render_template('demand_forecast.html')

# Route to handle demand forecasting
@app.route('/predict', methods=['POST'])
def predict():
    subprocess.run(['python3', 'generate_forecast.py'])
    return redirect(url_for('demand_forecast'))

@app.route('/demand_forecast')
def demand_forecast():
    try:
        forecast_df = pd.read_csv('static/forecast.csv')
        table_html = forecast_df.to_html(classes='table table-bordered', index=False)
    except FileNotFoundError:
        table_html = None
    return render_template("demand_forecast.html", forecast_table=table_html)

# Routes for Carbon Emissions Prediction
@app.route('/carbon_emission')
def carbon_emission():
    return render_template('carbon_emission.html')

@app.route('/predict_carbon', methods=['POST'])
def predict_carbon():
    # Process uploaded carbon emission data
    if 'carbon_file' not in request.files:
        return 'No file part', 400
    file = request.files['carbon_file']
    if file.filename == '':
        return 'No selected file', 400
    file.save(f'uploads/carbon_data/{file.filename}')

    # Run the carbon emissions prediction script
    subprocess.run(['python3', 'predict_carbon.py', f'uploads/carbon_data/{file.filename}'])
    
    return redirect(url_for('carbon_emission_result'))

@app.route('/carbon_emission_result')
def carbon_emission_result():
    try:
        result_df = pd.read_csv('static/forecasts/carbon_emissions_forecast.csv')
        table_html = result_df.to_html(classes='table table-bordered', index=False)
    except FileNotFoundError:
        table_html = None
    return render_template("carbon_emission_result.html", carbon_table=table_html)

# Route to handle user login and registration
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    fullname = request.form['fullname']
    
    if add_user(username, password, email, fullname):
        return redirect(url_for('index'))
    return 'Registration Failed', 400

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if verify_user(username, password):
        return redirect(url_for('index'))
    return 'Login Failed', 400

if __name__ == '__main__':
    app.run(debug=True)
