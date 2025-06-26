import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import './App.css';

function App() {
  const [ticker, setTicker] = useState('');
  const [forecast, setForecast] = useState([]);
  const [error, setError] = useState('');
  const [rmse, setRmse] = useState(null);
  const [yTrue, setYTrue] = useState([]);
  const [yPred, setYPred] = useState([]);
  const [name, setName] = useState('');
  const [suggestion, setSuggestion] = useState('');
  const [change, setChange] = useState(null);
  const [stockInfo, setStockInfo] = useState({});
  const [loading, setLoading] = useState(false);


  const getForecast = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`https://stock-prediction-dr3c.onrender.com/forecast/${ticker}`);
      const data = res.data.data;
      if (data.error) {
        setError(data.error)
        return;
      }
      setForecast(data.forecast);
      setRmse(data.rmse);
      setYTrue(data.y_true);
      setYPred(data.y_pred);
      setName(data.name);
      setSuggestion(data.suggestion);
      setChange(data.return);
      setStockInfo(data.stock_info);
      setError('');
    } catch (err) {
      setError('Server error');
    }
    setLoading(false);
  };

  const predictionData = yTrue.map((trueVal, i) => ({
    index: i + 1,
    Actual: trueVal,
    Predicted: yPred[i]
  }));

  return (
    <div className="App">
      <h2>Stock Forecast Accuracy</h2>

      <div clasName="input-group">
        <input
          type="text"
          value={ticker}
          onChange={e => setTicker(e.target.value.toUpperCase())}
          placeholder="Enter stock ticker (e.g. AAPL)"
          className="input-style"
        />
        <button className="submit-btn" onClick={getForecast}>Get Forecast</button>
      </div>

      {loading && (
        <div className="loading-bar-container">
          <div className="spinner" />
        </div>
      )}

      {error && <p style={{ color: "red" }}>{error}</p>}

      {Object.keys(stockInfo).length > 0 && (
        <div className="sidebar">
          <h3>Stock Information</h3>
          <ul>
            {Object.entries(stockInfo).map(([key, value]) => (
              <li key={key}>
                <strong>{key}: </strong> {value ? value.toLocaleString() : 'N/A'}
              </li>
            ))}
          </ul>
        </div>
      )}

      {yTrue.length > 0 && (
        <div className="graph">
          <h3>{name} Model Accuracy</h3>
          <LineChart width={600} height={300} data={predictionData}>
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="index" />
            <YAxis domain={['dataMin - 10', 'dataMin + 10']}/>
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Actual" stroke="#82ca9d" dot={false}/>
            <Line type="monotone" dataKey="Predicted" stroke="#7c8aff" dot={false}/>
          </LineChart>
        </div>
      )}

      {rmse !== null && (
        <div className="card-container">
          {/* RMSE Card */}
          <div className="card">
            <h4>📊 Model RMSE</h4>
            <p className="rmse-val">{rmse}</p>
          </div>

          {/* Forecast Card */}
          <div className="card">
            <h4>💲7-Day Forecast</h4>
            <ul className="forecast-list">
              {forecast.map((f, i) => (
                <li key={i}>
                  $ {f.price}
                </li>
              ))}
            </ul>
          </div>

          {/* Suggestion Card */}
          <div className="card">
            <h4>📈 Investment Suggestion</h4>
              <p
              style={{
                fontSize: '1.5rem',
                fontWeight: 'bold',
                color:
                  suggestion === 'Buy'
                    ? 'green'
                    : suggestion === 'Sell'
                    ? 'red'
                    : '#f1c40f',
              }}
            >
              {suggestion} ({change > 0 ? '+' : ''}
              {change}%) 
            </p>
          </div>
        </div>
      )}

      {forecast.length > 0 && (
        <div className="graph">
          <h3>7-Day Forecast Graph</h3>
          <LineChart width={600} height={300} data={forecast}>
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="day" label={{ value: 'Day', position: 'insideBottomRight', offset: -5 }} />
            <YAxis domain={['dataMin - 5', 'dataMin + 5']}/>
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="price" stroke="#007bff" strokeWidth={2} dot={false} name="Forecast" />
          </LineChart>
        </div>
      )}
    </div>
  );
}

export default App;

