import React, { useState, useEffect } from 'react'; // Use useEffect instead of React.useEffect
import axios from 'axios';
import '../StockPriceDisplay/StockPriceDisplay.css'; // Import component-specific styles
//import './App.css'; // Import global styles

const StockPriceDisplay = () => {
  // Use consistent indentation for better readability
  const [stockPrices, setStockPrices] = useState([]);

  useEffect(() => {
    const fetchStockPrices = async () => {
      try {
        const response = await axios.get('/api/stock-prices');
        setStockPrices(response.data);
      } catch (error) {
        console.error('Error fetching stock prices:', error); // Handle errors
      }
    };

    fetchStockPrices(); // Call the function to fetch data
  }, []);

  return (
    <div className="stock-price-display">
      <h1>Live Stock Prices</h1>
      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {stockPrices.map((price) => (
            <tr key={price.symbol}>
              <td>{price.symbol}</td>
              <td>{price.price}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StockPriceDisplay;