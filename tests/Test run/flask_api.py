from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def get_forecast():
    forecast = pd.read_csv("forecast.csv")
    return jsonify(forecast.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
