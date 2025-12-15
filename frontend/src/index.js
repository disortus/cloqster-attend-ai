import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import "./components/Navbar/Navbar.css";
import { BrowserRouter } from 'react-router-dom';
import './components/Navbar/Dropdown.css';
import "bootstrap/dist/css/bootstrap.min.css";

import { AuthProvider } from "./auth/AuthContext";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <AuthProvider>
                <App />
            </AuthProvider>
        </BrowserRouter>
    </React.StrictMode>
);

reportWebVitals();
