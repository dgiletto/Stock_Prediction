import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

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
    <div className="App" style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h2>Stock Forecast Accuracy</h2>

      <input
        type="text"
        value={ticker}
        onChange={e => setTicker(e.target.value.toUpperCase())}
        placeholder="Enter stock ticker (e.g. AAPL)"
        style={{ padding: "0.5rem", marginRight: "1rem" }}
      />
      <button onClick={getForecast}>Get Forecast</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {yTrue.length > 0 && (
        <>
          <h3>Model Accuracy</h3>
          <LineChart width={600} height={300} data={predictionData}>
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="index" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Actual" stroke="#82ca9d" />
            <Line type="monotone" dataKey="Predicted" stroke="#8884d8" />
          </LineChart>
        </>
      )}

      {rmse !== null && (
        <div style={{ marginTop: "2rem", display: "flex", gap: "2rem" }}>
          {/* RMSE Card */}
          <div style={{
            border: "1px solid #ddd", borderRadius: "10px", padding: "1rem", width: "200px", boxShadow: "0px 2px 4px rgba(0,0,0,0.1)"
          }}>
            <h4>Model RMSE</h4>
            <p style={{ fontSize: "1.5rem", color: "#444" }}>{rmse}</p>
          </div>

          {/* Forecast Card */}
          <div style={{
            border: "1px solid #ddd", borderRadius: "10px", padding: "1rem", width: "300px", boxShadow: "0px 2px 4px rgba(0,0,0,0.1)"
          }}>
            <h4>7-Day Forecast</h4>
            <ul style={{ paddingLeft: "1rem" }}>
              {forecast.map((f, i) => (
                <li key={i}>
                  Day {f.day}: ${f.price}
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

