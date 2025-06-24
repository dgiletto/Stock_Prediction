import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras import Sequential
from keras.layers import LSTM, Dense
from math import sqrt

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
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(lookback, len(feature_cols))))
    model.add(LSTM(32))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=10, batch_size=16, verbose=0)

    # Predict test
    y_pred_scaled = model.predict(X_test, verbose=0)

    # Inverse transform test predictions
    dummy_pred = np.zeros((len(y_pred_scaled), len(feature_cols)))
    dummy_true = np.zeros((len(y_test), len(feature_cols)))
    dummy_pred[:, 3] = y_pred_scaled[:, 0]
    dummy_true[:, 3] = y_test

    y_pred_actual = scaler.inverse_transform(dummy_pred)[:, 3]
    y_true_actual = scaler.inverse_transform(dummy_true)[:, 3]
    rmse = sqrt(mean_squared_error(y_true_actual, y_pred_actual))

    # Forecast 7 future days
    last_seq = scaled_data[-lookback:]
    predictions = []
    for _ in range(7):
        input_seq = last_seq.reshape(1, lookback, len(feature_cols))
        pred_scaled = float(model.predict(input_seq, verbose=0).squeeze())
        new_row = last_seq[-1].copy()
        new_row[3] = pred_scaled
        last_seq = np.vstack([last_seq[1:], new_row])
        predictions.append(pred_scaled)

    # Inverse scale forecasted close prices
    dummy_forecast = np.zeros((7, len(feature_cols)))
    dummy_forecast[:, 3] = predictions
    forecast_close = scaler.inverse_transform(dummy_forecast)[:, 3]

    forecast = [{"day": len(df) + i + 1, "price": round(float(p), 2)} for i, p in enumerate(forecast_close)]

    return {
        "rmse": round(rmse, 2),
        "forecast": forecast,
        "y_pred": [round(p, 2) for p in y_pred_actual.tolist()],
        "y_true": [round(t, 2) for t in y_true_actual.tolist()]
    }