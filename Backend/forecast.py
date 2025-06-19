import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def fetch_stock_data(ticker):
    data = yf.download(ticker, period="60d", interval="1d")
    data = data[["Close"]].dropna().reset_index()
    data["Days"] = np.arange(len(data))
    return data

def forecast_7_day(ticker):
    data = fetch_stock_data(ticker)
    X = data[["Days"]]
    y = data["Close"]

    model = LinearRegression()
    model.fit(X, y)

    next_days = np.arange(len(data), len(data) + 7).reshape(-1, 1)
    forecast = model.predict(next_days)
    return [{"day": int(day[0]), "price": round(float(price), 2)}
        for day, price in zip(next_days, forecast)]
