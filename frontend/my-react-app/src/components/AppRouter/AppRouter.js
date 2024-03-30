import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import WelcomePage from '../WelcomePage/WelcomePage';
import Dashboard from '../Dashboard/Dashboard';
import LoginPage from '../LoginPage/LoginPage';
import SignupPage from '../SignupPage/SignupPage'; // Import SignupPage component
//import UserProfile from '../UserProfile/UserProfile'; // Example of another nested route

const AppRouter = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<WelcomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/dashboard" element={<Dashboard />}>
          
        </Route>
      </Routes>
    </Router>
  );
};

export default AppRouter;