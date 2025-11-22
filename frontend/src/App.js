import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import ReposList from './pages/ReposList';
import AccountsList from './pages/AccountsList';
import RepoDetail from './pages/RepoDetail';
import './App.css';

function Navigation() {
  const location = useLocation();

  return (
    <nav className="app-nav">
      <div className="nav-container">
        <Link to="/" className="nav-logo">Knowledge Repo</Link>
        <div className="nav-links">
          <Link
            to="/"
            className={location.pathname === '/' ? 'nav-link active' : 'nav-link'}
          >
            Repositories
          </Link>
          <Link
            to="/accounts"
            className={location.pathname === '/accounts' ? 'nav-link active' : 'nav-link'}
          >
            Accounts
          </Link>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<ReposList />} />
            <Route path="/accounts" element={<AccountsList />} />
            <Route path="/repos/:id" element={<RepoDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
