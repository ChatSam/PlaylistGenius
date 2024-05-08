import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import Callback from './components/Callback';
import Dashboard from './components/Dashboard';
import Categorize from './components/Categorize';
import Categories from './components/Categories';
import './global.css';

function App() {
    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/callback" element={<Callback />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/categorize/:playlistId" element={<Categorize />} />
                    <Route path="/categories/:playlistId" element={<Categories />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
