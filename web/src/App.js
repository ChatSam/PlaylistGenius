import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import Callback from './components/Callback';
import Dashboard from './components/Dashboard'; // Hypothetical component after login

function App() {
    return (
        <Router>
            <div className="App">
                <Routes> {/* Use Routes instead of Switch */}
                    <Route path="/" element={<LandingPage />} exact />
                    <Route path="/callback" element={<Callback />} />
                    <Route path="/dashboard" element={<Dashboard />} />
                    {/* other routes */}
                </Routes>
            </div>
        </Router>
    );
}

export default App;
