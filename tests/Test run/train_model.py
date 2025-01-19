import pandas as pd
from prophet import Prophet

# Load data
df = pd.read_csv("oil_demand_data.csv")
sentiment_df = pd.read_csv("sentiment_data.csv")

# Merge sentiment scores into the dataset
df["date"] = pd.to_datetime(df["date"])
sentiment_df["date"] = pd.to_datetime(sentiment_df["date"])
df = pd.merge(df, sentiment_df, on="date", how="left").fillna(0)

# Prepare data for Prophet
df.rename(columns={"date": "ds", "oil_price": "y"}, inplace=True)

# Train the model
model = Prophet()
model.add_regressor("sentiment_score")
model.fit(df)

# Make future predictions
future = model.make_future_dataframe(periods=14)
future = pd.merge(future, sentiment_df, on="ds", how="left").fillna(0)

forecast = model.predict(future)
forecast[["ds", "yhat"]].to_csv("forecast.csv", index=False)
