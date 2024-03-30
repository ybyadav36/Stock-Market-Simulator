import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import StockPriceDisplay from '../StockPriceDisplay/StockPriceDisplay';
import TrendGraphs from '../TrendGraphs/TrendGraphs';
import AnalysisPage from '../HistoricalDataAnalysis/AnalysisPage';
import LoginPage from '../LoginPage/LoginPage';
import WelcomePage from '../WelcomePage/WelcomePage';
import '../Dashboard/Dashboard.css';

const PrivateRoute = ({ children, isAuthenticated }) => {
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

const Dashboard = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userData, setUserData] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.get('/api/check-auth', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => {
          if (response.data.authenticated) {
            setIsAuthenticated(true);
            setUserData(response.data.user); // Store user data
          }
        })
        .catch((error) => {
          setError('Error validating authentication'); // Handle error
        });
    }
  }, []);

  const handleLogout = async () => {
    try {
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      setError(null);
      navigate('/login', { replace: true });
    } catch (error) {
      setError('Logout failed. Please try again.'); // Handle logout error
    }
  };

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <nav>
        <ul>
          <li>
            <Link to="/welcome">Welcome</Link>
          </li>
          <li>
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <Link to="/stock-price">Stock Price</Link>
            </PrivateRoute>
          </li>
          <li>
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <Link to="/trend-graphs">Trend Graphs</Link>
            </PrivateRoute>
          </li>
          <li>
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <Link to="/analysis">Analysis</Link>
            </PrivateRoute>
          </li>
          {!isAuthenticated && (
            <li>
              <Link to="/login">Log In</Link>
            </li>
          )}
          {isAuthenticated && (
            <li>
              <button type="button" onClick={handleLogout}>
                Log Out
              </button>
            </li>
          )}
        </ul>
      </nav>
      <Routes>
        <Route path="/welcome" element={<WelcomePage />} />
        <Route
          path="/stock-price"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <StockPriceDisplay userData={userData} />
            </PrivateRoute>
          }
        />
        <Route
          path="/trend-graphs"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <TrendGraphs />
            </PrivateRoute>
          }
        />
        <Route
          path="/analysis"
          element={
            <PrivateRoute isAuthenticated={isAuthenticated}>
              <AnalysisPage />
            </PrivateRoute>
          }
        />
        <Route path="/login" element={<LoginPage setIsAuthenticated={setIsAuthenticated} />} />
        <Route path="/*" element={<Navigate to="/welcome" replace />} />
      </Routes>
      {error && <p className="error-message">{error}</p>}
    </div>
  );
};

export default Dashboard;