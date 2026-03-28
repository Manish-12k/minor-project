import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import UIDSILoginPage from './UIDSILoginPage';
import AdminDashboard from './AdminDashboard';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Check if this is admin dashboard route
const pathname = window.location.pathname;
const isAdmin = pathname.includes('admin-dashboard');

root.render(
  <React.StrictMode>
    {isAdmin ? <AdminDashboard /> : <UIDSILoginPage />}
  </React.StrictMode>
);