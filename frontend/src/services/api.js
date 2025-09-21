import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth token management
let authToken = null;
let tenantSubdomain = null;

export const setAuthToken = (token) => {
  authToken = token;
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const setTenantContext = (subdomain) => {
  tenantSubdomain = subdomain;
  if (subdomain) {
    api.defaults.headers.common['X-Tenant'] = subdomain;
  } else {
    delete api.defaults.headers.common['X-Tenant'];
  }
};

// Initialize auth from localStorage
const initializeAuth = () => {
  const token = localStorage.getItem('auth_token');
  const tenant = localStorage.getItem('tenant_data');
  
  if (token) {
    setAuthToken(token);
  }
  
  if (tenant) {
    try {
      const tenantData = JSON.parse(tenant);
      setTenantContext(tenantData.subdomain);
    } catch (error) {
      console.error('Error parsing tenant data:', error);
    }
  }
};

// Initialize on module load
initializeAuth();

// Request interceptor to ensure auth headers are always fresh
api.interceptors.request.use(
  (config) => {
    // Ensure fresh token on each request
    const currentToken = localStorage.getItem('auth_token');
    if (currentToken && currentToken !== authToken) {
      setAuthToken(currentToken);
    }
    
    // Ensure fresh tenant context
    const currentTenant = localStorage.getItem('tenant_data');
    if (currentTenant) {
      try {
        const tenantData = JSON.parse(currentTenant);
        if (tenantData.subdomain !== tenantSubdomain) {
          setTenantContext(tenantData.subdomain);
        }
      } catch (error) {
        console.error('Error parsing tenant data in interceptor:', error);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 unauthorized errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await authAPI.refreshToken(refreshToken);
          const { access_token } = response.data;
          
          // Update stored token
          localStorage.setItem('auth_token', access_token);
          setAuthToken(access_token);
          
          // Retry original request
          originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          console.error('Token refresh failed:', refreshError);
          localStorage.clear();
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication API calls
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  refreshToken: (refresh_token) => api.post('/auth/refresh', { refresh_token }),
  getCurrentUser: () => api.get('/users/me'),
};

// Tenant API calls
export const tenantAPI = {
  create: (tenantData) => api.post('/tenants', tenantData),
  getCurrent: () => api.get('/tenant'),
  update: (tenantData) => api.put('/tenant', tenantData),
  getUsers: () => api.get('/users'),
  updateUser: (userId, userData) => api.put(`/users/${userId}`, userData),
  inviteUser: (inviteData) => api.post('/invitations', inviteData),
  getInvitations: () => api.get('/invitations'),
  acceptInvitation: (acceptanceData) => api.post('/invitations/accept', acceptanceData),
};

// Agent API calls (updated to work with multi-tenant backend)
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

// Task API calls (updated to work with multi-tenant backend)
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