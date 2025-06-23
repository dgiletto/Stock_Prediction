import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def fetch_stock_data(ticker):
    data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data[["Open", "High", "Low", "Volume", "Close"]].dropna().reset_index()

    # Basic Features
    data["Days"] = np.arange(len(data))
    data["Return"] = data["Close"].pct_change()

    # Technical Features
    data["MA_5"] = data["Close"].rolling(window=5).mean()
    data["MA_10"] = data["Close"].rolling(window=10).mean()
    data["Volatility_5"] = data["Close"].rolling(window=5).std()

    feature_cols = ["Days", "Open", "High", "Low", "Volume", "Return", "MA_5", "MA_10", "Volatility_5"]
    data = data.dropna(subset=feature_cols).reset_index(drop=True)

    return data

def forecast_30_day(ticker):
    data = fetch_stock_data(ticker)

    feature_cols = ["Days", "Open", "High", "Low", "Volume", "Return", "MA_5", "MA_10", "Volatility_5"]
    X = data[feature_cols]
    y = data["Close"]

    model = LinearRegression()
    model.fit(X, y)

    last_row = data.iloc[-1].copy()
    current_day = int(last_row["Days"])

    past_closes = list(data["Close"].tail(10))
    forecasts = []

    for i in range(1, 31):
        current_day += 1

        prev_close = past_closes[-1]
        simulated_close = prev_close + np.random.normal(0, 1)
        past_closes.append(simulated_close)
        if len(past_closes) > 10:
            past_closes.pop(0)
        
        future_row = last_row.copy()
        future_row["Days"] = current_day
        future_row["Close"] = simulated_close
        future_row["Return"] = (simulated_close / prev_close) - 1
        future_row["MA_5"] = np.mean(past_closes[-5:])
        future_row["MA_10"] = np.mean(past_closes)
        future_row["Volatility_5"] = np.std(past_closes[-5:])

        row_features = {col: future_row[col] for col in feature_cols}
        forecasts.append(row_features)

    
    X_future = pd.DataFrame(forecasts)
    y_pred = model.predict(X_future)

    return [{"day": int(row["Days"]), "price": round(float(price), 2)}
        for row, price in zip(X_future.to_dict(orient="records"), y_pred)]
