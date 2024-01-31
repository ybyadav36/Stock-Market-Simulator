import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import StockPriceDisplay from './components/StockPriceDisplay';
import TrendGraphs from './components/TrendGraphs';
import LoginPage from './components/LoginPage';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route path="/stock-price" element={<StockPriceDisplay />} />
          <Route path="/trend-graphs" element={<TrendGraphs />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<StockPriceDisplay />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;