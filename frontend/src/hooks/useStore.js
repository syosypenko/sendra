import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => set({ user: null, isAuthenticated: false })
}));

export const useEmailStore = create((set) => ({
  emails: [],
  selectedEmail: null,
  filters: {
    language: null,
    position: null,
    company: null,
    status: null,
    job_type: null,
    page: 1,
    limit: 20
  },
  setEmails: (emails) => set({ emails }),
  setSelectedEmail: (email) => set({ selectedEmail: email }),
  setFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters }
  }))
}));

export const useAnalyticsStore = create((set) => ({
  dashboard: null,
  byStatus: [],
  byJobType: [],
  byExperience: [],
  applicationFunnel: null,
  topCompanies: [],
  topPositions: [],
  stats: null,
  loading: false,
  
  setDashboard: (data) => set({ dashboard: data }),
  setByStatus: (data) => set({ byStatus: data }),
  setByJobType: (data) => set({ byJobType: data }),
  setByExperience: (data) => set({ byExperience: data }),
  setApplicationFunnel: (data) => set({ applicationFunnel: data }),
  setTopCompanies: (data) => set({ topCompanies: data }),
  setTopPositions: (data) => set({ topPositions: data }),
  setStats: (data) => set({ stats: data }),
  setLoading: (loading) => set({ loading })
}));
