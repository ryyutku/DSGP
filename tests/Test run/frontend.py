import dash
from dash import dcc, html
import pandas as pd
import requests
import plotly.express as px

# Load predictions from Flask API
response = requests.get("http://127.0.0.1:5000/predict")
data = response.json()
df = pd.DataFrame(data)

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Oil Demand Forecast - Colombo"),
    dcc.Graph(figure=px.line(df, x="ds", y="yhat", title="Predicted Oil Demand")),
])

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
