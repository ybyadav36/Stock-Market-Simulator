import React, { useState, useEffect } from 'react';
import Ticker from 'react-ticker';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';

const STOCK_PRICE_URL = 'https://your-backend-api.com/current-price';
const STOCK_HISTORY_URL = 'https://your-backend-api.com/historical-data';

const StockPriceDisplay = () => {
  const [currentPrice, setCurrentPrice] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);

  useEffect(() => {
    fetch(STOCK_PRICE_URL)
      .then((response) => response.json())
      .then((data) => setCurrentPrice(data.price));

    fetch(STOCK_HISTORY_URL)
      .then((response) => response.json())
      .then((data) => setHistoricalData(data));
  }, []);

  return (
    <div>
      <Ticker>
        Current Price: ${currentPrice || 'Loading...'}
      </Ticker>
      <LineChart width={500} height={300} data={historicalData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
        <Line type="monotone" dataKey="price" stroke="#8884d8" />
        <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
      </LineChart>
    </div>
  );
};

export default StockPriceDisplay;