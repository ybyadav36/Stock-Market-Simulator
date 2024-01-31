import React, { useState, useEffect } from 'react';
import { BarChart, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, Line } from 'recharts';

const STOCK_HISTORY_URL = 'https://your-backend-api.com/historical-data';

const TrendGraphs = () => {
  const [historicalData, setHistoricalData] = useState([]);

  useEffect(() => {
    // Fetch historical data from the API and set it using setHistoricalData
  }, []);

  return (
    <div>
      <h2>Historical Data</h2>
      <LineChart width={500} height={300} data={historicalData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <XAxis dataKey="date" />
        <YAxis />
        <CartesianGrid strokeDasharray="3 3" />
        <Tooltip />
        <Line type="monotone" dataKey="price" stroke="#8884d8" activeDot={{ r: 8 }} />
      </LineChart>
    </div>
  );
};

export default TrendGraphs;