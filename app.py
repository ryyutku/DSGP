Integrate inventory management functions into Flask app, including data processing, forecasting, plotting, and email alerts.

This commit integrates the inventory management functions into a Flask web application.

Key changes:
- Integrated data loading and preprocessing.
- Added ARIMA and Random Forest model training and forecasting.
- Implemented stock level plotting and embedding into the web page.
- Added email alert functionality for low stock levels.
- Used environment variables for sensitive data.
- Added Matplotlib Agg backend to prevent GUI errors.
