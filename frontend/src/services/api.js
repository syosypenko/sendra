import axios from 'axios';

// Ensure base URL always includes /api to work behind nginx proxy at http://localhost
let API_URL = process.env.REACT_APP_API_URL || '/api';
if (!API_URL.endsWith('/api')) {
  API_URL = `${API_URL.replace(/\/$/, '')}/api`;
}

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true
});

export const authService = {
  login: async () => {
    const response = await api.get('/auth/google');
    window.location.href = response.data.authorization_url;
  },
  exchangeCode: (code) => api.post('/auth/google/exchange', { code }),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me')
};

export const emailService = {
  getEmails: (params) => api.get('/emails', { params }),
  getEmailById: (id) => api.get(`/emails/${id}`),
  updateEmail: (id, data) => api.patch(`/emails/${id}`, data),
  deleteEmail: (id) => api.delete(`/emails/${id}`)
};

export const gmailSyncService = {
  naturalQuery: (prompt, limit = 50, include_gmail_fetch = true) =>
    api.post('/gmail/natural-query', { prompt, limit, include_gmail_fetch }),
  syncEmails: (prompt = '') => api.post('/gmail/sync', { prompt })
};

export const analyticsService = {
  getDashboardSummary: () => api.get('/analytics/dashboard-summary'),
  getByStatus: () => api.get('/analytics/by-status'),
  getByJobType: () => api.get('/analytics/by-job-type'),
  getByExperience: () => api.get('/analytics/by-experience'),
  getApplicationFunnel: () => api.get('/analytics/application-funnel'),
  getTopCompanies: (limit = 10) => api.get('/analytics/top-companies', { params: { limit } }),
  getTopPositions: (limit = 10) => api.get('/analytics/top-positions', { params: { limit } }),
  getStats: () => api.get('/analytics/stats')
};

export const collectionService = {
  create: (name, emails) => {
    console.log('📤 Sending to POST /collections:', { name, emailCount: emails.length, firstEmail: emails[0] });
    return api.post('/collections', { name, emails });
  },
  list: () => api.get('/collections'),
  get: (id) => api.get(`/collections/${id}`),
  delete: (id) => {
    console.log('🗑️ Deleting collection:', id);
    return api.delete(`/collections/${id}`);
  }
};

export default api;
