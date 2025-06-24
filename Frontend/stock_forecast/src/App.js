import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import './App.css';

function App() {
  const [ticker, setTicker] = useState('');
  const [forecast, setForecast] = useState([]);
  const [error, setError] = useState('');
  const [rmse, setRmse] = useState(null);
  const [yTrue, setYTrue] = useState([])
  const [yPred, setYPred] = useState([])


  const getForecast = async () => {
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
      setError('');
    } catch (err) {
      setError('Server error');
    }
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

      {error && <p style={{ color: "red" }}>{error}</p>}

      {yTrue.length > 0 && (
        <div className="graph">
          <h3>{ticker} Model Accuracy</h3>
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
            <h4>Model RMSE</h4>
            <p className="rmse-val">{rmse}</p>
          </div>

          {/* Forecast Card */}
          <div className="card">
            <h4>7-Day Forecast</h4>
            <ul className="forecast-list">
              {forecast.map((f, i) => (
                <li key={i}>
                  ${f.price}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

