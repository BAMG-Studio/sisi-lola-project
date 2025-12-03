import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v2';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
  logout: () => {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  }
};

export const controlAPI = {
  getDashboard: () => api.get('/control/analytics/dashboard'),
  getAssets: (params?: any) => api.get('/control/assets', { params }),
  createAsset: (data: any) => api.post('/control/assets', data),
  getContentQueue: (params?: any) => api.get('/control/content/queue', { params }),
  addToQueue: (data: any) => api.post('/control/content/queue', data),
  approveContent: (id: number) => api.put(`/control/content/${id}/approve`),
  publishContent: (id: number) => api.post(`/control/content/${id}/publish`),
  getMLJobs: () => api.get('/control/ml/jobs'),
  triggerTraining: (data: any) => api.post('/control/ml/train', data),
  getPlatforms: () => api.get('/control/platforms')
};

export default api;
