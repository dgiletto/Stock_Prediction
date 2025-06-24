import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function App() {
  const [ticker, setTicker] = useState('');
  const [forecast, setForecast] = useState([]);
  const [error, setError] = useState('');

  const getForecast = async () => {
    try {
      const res = await axios.get(`https://stock-prediction-dr3c.onrender.com/forecast/${ticker}`);
      if (res.data.forecast) {
        setForecast(res.data.forecast);
        setError('');
      } else {
        setError(res.data.error || 'Unknown error');
        setForecast([]);
      }
    } catch (err) {
      setError('Server error');
    }
  };

  return (
    <div className="App" style={{ padding: "2rem" }}>
      <h2>Stock Forecast</h2>
      <input
        type="text"
        value={ticker}
        onChange={e => setTicker(e.target.value.toUpperCase())}
        placeholder="Enter stock ticker (e.g. AAPL)"
      />
      <button onClick={getForecast}>Get Forecast</button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {forecast.length > 0 && (
        <LineChart width={600} height={300} data={forecast}>
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="day" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="price" stroke="#8884d8" />
        </LineChart>
      )}
    </div>
  );
}

export default App;

