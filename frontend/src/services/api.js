import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Agent API calls
export const agentAPI = {
  getAll: (params = {}) => api.get('/agents', { params }),
  getById: (id) => api.get(`/agents/${id}`),
  create: (data) => api.post('/agents', data),
  update: (id, data) => api.put(`/agents/${id}`, data),
  delete: (id) => api.delete(`/agents/${id}`),
  start: (id) => api.post(`/agents/${id}/start`),
  stop: (id) => api.post(`/agents/${id}/stop`),
  getTasks: (id, params = {}) => api.get(`/agents/${id}/tasks`, { params }),
};

// Task API calls
export const taskAPI = {
  getAll: (params = {}) => api.get('/tasks', { params }),
  getById: (id) => api.get(`/tasks/${id}`),
  create: (data) => api.post('/tasks', data),
  execute: (id) => api.post(`/tasks/${id}/execute`),
};

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;