import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

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

export default api;
