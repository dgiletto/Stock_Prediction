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
    df = yf.download(ticker, period="2y", interval="1d", auto_adjust=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    if len(df) < 90:
        raise ValueError("Not enough data to forecast.")

    feature_cols = ["Open", "High", "Low", "Close", "Volume"]

    # Scale Input Features
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[feature_cols])

    # Scale Close Seperately
    close_scaler = MinMaxScaler()
    scaled_close = close_scaler.fit_transform(df[["Close"]])

    # Create sequences
    lookback = 60
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i])
        y.append(scaled_close[i])
    X, y = np.array(X), np.array(y)

    # Train Test Split
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # LSTM Model
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(lookback, len(feature_cols))),
        GaussianNoise(0.01),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    # Train with early stop
    early_stop = EarlyStopping(patience=5, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=50, batch_size=16, verbose=0, validation_split=0.1, callbacks=[early_stop])

    # Predict test
    y_pred_scaled = model.predict(X_test, verbose=0)
    y_pred_actual = close_scaler.inverse_transform(y_pred_scaled).flatten()
    y_true_actual = close_scaler.inverse_transform(y_test).flatten()
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

        dummy = np.zeros((1, len(feature_cols)))
        dummy[0, 3] = pred_scaled
        forecast_price = float(close_scaler.inverse_transform(dummy)[0, 0])
        predictions.append(round(forecast_price, 2))
    
    forecast = [{"day": len(df) + i + 1, "price": p} for i, p in enumerate(predictions)]

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