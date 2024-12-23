import React from 'react';
import ReactDOM from 'react-dom/client'; // React 18以降の公式推奨
import App from './App';
import './App.css';

// React 18での適切なレンダリング
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);