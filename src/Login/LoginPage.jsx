
import React, { useState, useContext } from 'react';
import styles from './LoginPage.module.css';
import { AuthContext } from '../AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import Footer from '../Footer/Footer';
import logoImage from '../assets/logo.PNG'; // Make sure to add your logo file

const LoginPage = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [error, setError] = useState('');
  const { login, register } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  React.useEffect(() => {
    const params = new URLSearchParams(location.search);
    const tab = params.get('tab');
    if (tab === 'register') {
      setActiveTab('register');
    }
  }, [location]);

  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerName, setRegisterName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');

  const handleLoginSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (login(loginEmail, loginPassword)) {
      navigate('/');
    } else {
      setError('Invalid email or password');
    }
  };

  const handleRegisterSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (register(registerName, registerEmail, registerPassword)) {
      navigate('/');
    } else {
      setError('Email already registered');
    }
  };

  return (
    <div className={styles.loginWrapper}>
      <div className={styles.loginContainer}>
        <div className={styles.logoContainer}>
          <img src={logoImage} alt="TravelMate Logo" className={styles.logo} />
          <p className={styles.tagline}>TRAVEL MORE, SPEND LESS</p>
        </div>

        <div className={styles.tabs}>
          <button
            className={`${styles.tabButton} ${activeTab === 'login' ? styles.active : ''}`}
            onClick={() => {
              setActiveTab('login');
              setError('');
            }}
          >
            Login
          </button>
          <button
            className={`${styles.tabButton} ${activeTab === 'register' ? styles.active : ''}`}
            onClick={() => {
              setActiveTab('register');
              setError('');
            }}
          >
            Register
          </button>
        </div>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <div className={styles.tabContent}>
          {activeTab === 'login' ? (
            <form onSubmit={handleLoginSubmit} className={styles.form}>
              <div className={styles.formGroup}>
                <label htmlFor="loginEmail">Email</label>
                <input
                  type="email"
                  id="loginEmail"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="loginPassword">Password</label>
                <input
                  type="password"
                  id="loginPassword"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className={styles.submitButton}>
                Sign In
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegisterSubmit} className={styles.form}>
              <div className={styles.formGroup}>
                <label htmlFor="registerName">Name</label>
                <input
                  type="text"
                  id="registerName"
                  value={registerName}
                  onChange={(e) => setRegisterName(e.target.value)}
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="registerEmail">Email</label>
                <input
                  type="email"
                  id="registerEmail"
                  value={registerEmail}
                  onChange={(e) => setRegisterEmail(e.target.value)}
                  required
                />
              </div>
              <div className={styles.formGroup}>
                <label htmlFor="registerPassword">Password</label>
                <input
                  type="password"
                  id="registerPassword"
                  value={registerPassword}
                  onChange={(e) => setRegisterPassword(e.target.value)}
                  required
                />
              </div>
              <button type="submit" className={styles.submitButton}>
                Sign Up
              </button>
            </form>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default LoginPage;