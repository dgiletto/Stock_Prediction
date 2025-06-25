import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from math import sqrt
from pmdarima import auto_arima

def get_stock_name(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("longName", "Unknown Company")
    except Exception as e:
        return "Unknown Company"

def generate_suggestion(forecast):
    prices = [day["price"] for day in forecast]
    start = prices[0]
    end = prices[-1]
    change = ((end - start) / start) * 100

    if change > 2:
        return "Buy", round(change, 2)
    elif change < -2:
        return "Sell", round(change, 2)
    else:
        return "Hold", round(change, 2)

def forecast_and_eval(ticker):
    df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True)

    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"][ticker]
    else:
        df = df["Close"]
    
    df = df.dropna()

    close_prices = df.squeeze()
    train_size = int(len(close_prices) * 0.8)
    train, test = close_prices[:train_size], close_prices[train_size:]

    model = auto_arima(train,
                       start_p=0, max_p=5,
                       start_q=0, max_q=5,
                       seasonal=False,
                       stepwise=True,
                       suppress_warnings=True,
                       error_action='ignore')

    # Predict on test set
    forecast_test = model.predict(n_periods=len(test))
    rmse = sqrt(mean_squared_error(test, forecast_test))

    # Forecast next 7 days
    model.update(close_prices)
    forecast_7d = model.predict(n_periods=7)
    forecast = [{"day": len(df) + i + 1, "price": round(float(p), 2)} for i, p in enumerate(forecast_7d)]

    suggestion, change = generate_suggestion(forecast)

    return {
        "rmse": round(rmse, 2),
        "forecast": forecast,
        "y_pred": [round(float(p), 2) for p in forecast_test],
        "y_true": [round(float(t), 2) for t in test],
        "name": get_stock_name(ticker),
        "suggestion": suggestion,
        "return": change
    }