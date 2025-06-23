import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras import Sequential
from keras.layers import LSTM, Dense

def forecast_30_day(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
    df = df[["Close"]].dropna()
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df)

    lookback = 60
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i])
        y.append(scaled_data[i])
    X, y = np.array(X), np.array(y)

    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, batch_size=16, verbose=0)

    last_60 = scaled_data[-lookback:].reshape(1, lookback, 1)
    predictions = []

    for _ in range(30):
        next_pred = model.predict(last_60, verbose=0)[0][0]
        predictions.append(next_pred)
        last_60 = np.append(last_60[:, 1:, :], [[[next_pred]]], axis=1)
    
    predicted_prices = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

    start_day = len(df)
    forecast = [{"day": start_day + i + 1, "price": round(float(price[0]), 2)} for i, price in enumerate(predicted_prices)]

    return forecast

