import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from math import sqrt
from keras.layers import LSTM, Dense, Dropout, GaussianNoise
from keras.callbacks import EarlyStopping
from keras import Sequential

def get_stock_name(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("longName", "Unknown Company")
    except Exception as e:
        return "Unknown Company"

def get_stock_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            "Volume": info.get("volume"),
            "Open": info.get("open"),
            "High Today": info.get("dayHigh"),
            "Low Today": info.get("dayLow"),
            "Market Cap": info.get("marketCap"),
            "52 Week High": info.get("fiftyTwoWeekHigh"),
            "52 Week Low": info.get("fiftyTwoWeekLow"),
            "P/E Ratio": info.get("trailingPE")
        }
    except Exception:
        return {}

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
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    if len(df) < 90:
        raise ValueError("Not enough data to forecast.")

    feature_cols = ["Open", "High", "Low", "Close", "Volume"]

    # Scale data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[feature_cols])

    # Create sequences
    lookback = 60
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i])
        y.append(scaled_data[i][3])  # Close is at index 3
    X, y = np.array(X), np.array(y)

    # Train Test Split
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # LSTM Model
    model = Sequential([
        LSTM(32, return_sequences=False, input_shape=(lookback, len(feature_cols))),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=10, batch_size=16, verbose=0)

    # Predict test
    y_pred_scaled = model.predict(X_test, verbose=0)

    # Inverse transform test predictions
    dummy_pred = np.zeros((len(y_pred_scaled), len(feature_cols)))
    dummy_true = np.zeros((len(y_test), len(feature_cols)))
    dummy_pred[:, 3] = y_pred_scaled.squeeze()
    dummy_true[:, 3] = y_test.squeeze()

    y_pred_actual = scaler.inverse_transform(dummy_pred)[:, 3]
    y_true_actual = scaler.inverse_transform(dummy_true)[:, 3]
    rmse = sqrt(mean_squared_error(y_true_actual, y_pred_actual))

    # Forecast 7 future days
    num_samples = 100  # Number of Monte Carlo runs
    future_preds = []

    for _ in range(num_samples):
        last_seq = scaled_data[-lookback:]
        preds = []
        for _ in range(7):
            input_seq = last_seq.reshape(1, lookback, len(feature_cols))
            pred_scaled = float(model(input_seq, training=True).numpy().squeeze())
            new_row = last_seq[-1].copy()
            new_row[3] = pred_scaled
            last_seq = np.vstack([last_seq[1:], new_row])
            preds.append(pred_scaled)
        future_preds.append(preds)

    future_preds = np.array(future_preds)
    means = np.mean(future_preds, axis=0)
    stds = np.std(future_preds, axis=0)

    # Inverse scale
    dummy_forecast = np.zeros((7, len(feature_cols)))
    forecast = []

    for i in range(7):
        dummy_forecast[:, :] = 0  # Reset for each day
        dummy_forecast[i, 3] = means[i]
        mean_inv = scaler.inverse_transform(dummy_forecast)[i, 3]
        
        dummy_forecast[i, 3] = means[i] + 1.96 * stds[i]
        upper = scaler.inverse_transform(dummy_forecast)[i, 3]
        
        dummy_forecast[i, 3] = means[i] - 1.96 * stds[i]
        lower = scaler.inverse_transform(dummy_forecast)[i, 3]

        forecast.append({
            "day": len(df) + i + 1,
            "price": round(mean_inv, 2),
            "upper": round(upper, 2),
            "lower": round(lower, 2),
        })

    suggestion, change = generate_suggestion(forecast)

    return {
        "rmse": round(rmse, 2),
        "forecast": forecast,
        "y_pred": [round(p, 2) for p in y_pred_actual.tolist()],
        "y_true": [round(t, 2) for t in y_true_actual.tolist()],
        "name": get_stock_name(ticker),
        "suggestion": suggestion,
        "return": change,
        "stock_info": get_stock_info(ticker)
    }