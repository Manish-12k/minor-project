/** Backend API base URL (no trailing slash). Override with REACT_APP_API_URL at build time. */
const raw = process.env.REACT_APP_API_URL || 'http://localhost:8000';
export const API_BASE_URL = raw.replace(/\/+$/, '');
