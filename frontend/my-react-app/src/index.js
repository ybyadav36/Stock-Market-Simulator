import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from './components/LoginPage';
import StockPriceDisplay from './components/StockPriceDisplay';
import TrendGraphs from './components/TrendGraphs';

ReactDOM.render(
  <BrowserRouter>
    <Routes>
      <Route path="/stock-price" element={<StockPriceDisplay />} />
      <Route path="/trend-graphs" element={<TrendGraphs />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<StockPriceDisplay />} />
    </Routes>
  </BrowserRouter>,
  document.getElementById('root')
);