import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras import Sequential
from keras.layers import LSTM, Dense

def forecast_30_day(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    if len(df) < 90:
        raise ValueError("Not enough data to forecast.")

    feature_cols = ["Open", "High", "Low", "Close", "Volume"]

    # 2. Scale data
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[feature_cols])

    # 3. Create sequences
    lookback = 60
    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i])
        y.append(scaled_data[i][3])  # Close is at index 3
    X, y = np.array(X), np.array(y)

    # 4. LSTM Model
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(lookback, len(feature_cols))))
    model.add(LSTM(32))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, batch_size=16, verbose=0)

    # 5. Forecast next 30 days
    last_seq = scaled_data[-lookback:]
    predictions_scaled = []

    for _ in range(30):
        input_seq = last_seq.reshape(1, lookback, len(feature_cols))
        pred = model.predict(input_seq, verbose=0)
        pred_scalar = float(pred[0][0])  # Safe scalar extraction
        new_row = last_seq[-1].copy()
        new_row[3] = pred_scalar  # Update "Close"
        last_seq = np.vstack([last_seq[1:], new_row])
        predictions_scaled.append(pred_scalar)

    # 6. Inverse transform
    dummy = np.zeros((30, len(feature_cols)))
    dummy[:, 3] = predictions_scaled  # Only "Close" filled
    inverted = scaler.inverse_transform(dummy)
    predicted_close = inverted[:, 3]  # Extract only close prices

    # 7. Format result
    start_day = len(df)
    forecast = [{"day": start_day + i + 1, "price": round(float(price), 2)} for i, price in enumerate(predicted_close)]
    return forecast

