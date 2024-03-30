import React from 'react';
import { Link } from 'react-router-dom';
import '../WelcomePage/WelcomePage.css';

const WelcomePage = () => {
  return (
    <div className="welcome-page">
      <h1>Welcome to Geeks</h1>
      <p>This is your one-stop shop for all things awesome!</p>
      <div className="button-container">
        <Link to="/login">
          <button className="login-button">Log In</button>
        </Link>
        <Link to="/signup">
          <button className="signup-button">Sign Up</button>
        </Link>
      </div>
    </div>
  );
};

export default WelcomePage;