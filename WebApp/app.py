from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for demand forecasting page
@app.route('/demand_forecasting')
def demand_forecasting():
    return render_template('demand_forecasting.html')

# Route to handle PDF file upload
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'pdf_file' not in request.files:
        return 'No file part', 400
    file = request.files['pdf_file']
    if file.filename == '':
        return 'No selected file', 400
    # Save the file to the upload folder
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return 'PDF uploaded successfully!', 200

# Route to handle CSV file upload
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'csv_file' not in request.files:
        return 'No file part', 400
    file = request.files['csv_file']
    if file.filename == '':
        return 'No selected file', 400
    # Save the file to the upload folder
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    return 'CSV uploaded successfully!', 200

if __name__ == "__main__":
    app.run(debug=True)
