import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Security: Request ID for tracking and CSRF protection
const generateRequestId = () => Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

// Create axios instance with security headers
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest', // CSRF protection
  },
  timeout: 30000, // 30 second timeout
  withCredentials: false, // Don't send cookies for security
});

// Auth token management
let authToken = null;
let tenantSubdomain = null;

export const setAuthToken = (token) => {
  authToken = token;
  if (token) {
    console.log('🔑 API: Setting auth token:', token.substring(0, 20) + '...');
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    console.log('🚫 API: Clearing auth token');
    delete api.defaults.headers.common['Authorization'];
  }
};

export const setTenantContext = (subdomain) => {
  tenantSubdomain = subdomain;
  if (subdomain) {
    // Security: Use tenant header for multi-tenancy isolation
    api.defaults.headers.common['X-Tenant'] = subdomain;
  } else {
    delete api.defaults.headers.common['X-Tenant'];
  }
};

// Security: Input sanitization helper
const sanitizeInput = (input) => {
  if (typeof input === 'string') {
    return input.trim().slice(0, 10000); // Limit input length
  }
  return input;
};

// Security: Sanitize request data
const sanitizeRequestData = (data) => {
  if (!data || typeof data !== 'object') return data;
  
  const sanitized = {};
  Object.keys(data).forEach(key => {
    if (typeof data[key] === 'string') {
      sanitized[key] = sanitizeInput(data[key]);
    } else if (Array.isArray(data[key])) {
      sanitized[key] = data[key].map(item => 
        typeof item === 'string' ? sanitizeInput(item) : item
      );
    } else {
      sanitized[key] = data[key];
    }
  });
  
  return sanitized;
};

// Initialize auth from sessionStorage (matches AuthContext)
const initializeAuth = () => {
  const token = sessionStorage.getItem('auth_token');
  const tenant = sessionStorage.getItem('tenant_data');
  
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

// Request interceptor with security enhancements
api.interceptors.request.use(
  (config) => {
    // Add request ID for tracking
    config.headers['X-Request-ID'] = generateRequestId();
    
    // Ensure fresh token on each request
    const currentToken = sessionStorage.getItem('auth_token');
    if (currentToken && currentToken !== authToken) {
      console.log('🔄 API: Refreshing token from sessionStorage');
      setAuthToken(currentToken);
    }
    
    // Request logging removed for production
    
    // Ensure fresh tenant context
    const currentTenant = sessionStorage.getItem('tenant_data');
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
    
    // Security: Sanitize request data
    if (config.data) {
      config.data = sanitizeRequestData(config.data);
    }
    
    // Security: Validate URL to prevent SSRF
    const allowedHosts = ['localhost', '127.0.0.1', process.env.REACT_APP_API_HOST];
    const url = new URL(config.url, config.baseURL);
    if (!allowedHosts.some(host => url.hostname.includes(host))) {
      console.warn('Blocked request to unauthorized host:', url.hostname);
      return Promise.reject(new Error('Unauthorized request destination'));
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with enhanced security and error handling
api.interceptors.response.use(
  (response) => {
    // Security: Validate response structure
    if (response.data && typeof response.data === 'object') {
      // Log response for security monitoring (excluding sensitive data)
      // API response logging disabled for production
    }
    
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Security: Log failed requests for monitoring
    console.warn('API Request failed:', {
      status: error.response?.status,
      url: originalRequest?.url,
      method: originalRequest?.method,
      requestId: originalRequest?.headers?.['X-Request-ID']
    });
    
    // Handle 401 unauthorized errors with enhanced security
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Security: Clear auth data on authentication failure
      const refreshToken = sessionStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await authAPI.refreshToken(refreshToken);
          const { access_token, expires_in } = response.data;
          
          // Update stored token with expiry
          const expiryTime = Date.now() + ((expires_in || 3600) * 1000);
          sessionStorage.setItem('auth_token', access_token);
          sessionStorage.setItem('token_expiry', expiryTime.toString());
          setAuthToken(access_token);
          
          // Retry original request
          originalRequest.headers['Authorization'] = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, clear all auth data and redirect
          console.error('Token refresh failed:', refreshError);
          sessionStorage.clear();
          // TEMPORARILY DISABLED: window.location.href = '/login?reason=session_expired';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, clear data and redirect
        sessionStorage.clear();
        // TEMPORARILY DISABLED: window.location.href = '/login?reason=auth_required';
      }
    }
    
    // Handle 403 forbidden - insufficient permissions
    if (error.response?.status === 403) {
      console.error('Access forbidden - insufficient permissions');
      // TEMPORARILY DISABLED for debugging: window.location.href = '/unauthorized?reason=insufficient_permissions';
    }
    
    // Handle rate limiting
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || 60;
      console.warn(`Rate limited - retry after ${retryAfter} seconds`);
    }
    
    return Promise.reject(error);
  }
);

// Enhanced Authentication API calls with security validations
export const authAPI = {
  login: (credentials) => {
    // Security: Validate input
    if (!credentials.email || !credentials.password) {
      return Promise.reject(new Error('Missing required credentials'));
    }
    return api.post('/auth/login', sanitizeRequestData(credentials));
  },
  
  register: (userData) => {
    // Security: Validate registration data
    if (!userData.email || !userData.password || userData.password.length < 8) {
      return Promise.reject(new Error('Invalid registration data'));
    }
    return api.post('/auth/register', sanitizeRequestData(userData));
  },
  
  logout: () => api.post('/auth/logout'),
  
  refreshToken: (refresh_token) => {
    if (!refresh_token) {
      return Promise.reject(new Error('Missing refresh token'));
    }
    return api.post('/auth/refresh', { refresh_token });
  },
  
  getCurrentUser: () => api.get('/auth/me'),
  
  changePassword: (passwordData) => {
    if (!passwordData.currentPassword || !passwordData.newPassword) {
      return Promise.reject(new Error('Missing password data'));
    }
    return api.post('/auth/change-password', sanitizeRequestData(passwordData));
  }
};

// Enhanced Tenant API calls with security checks
export const tenantAPI = {
  create: (tenantData) => api.post('/tenants', sanitizeRequestData(tenantData)),
  getCurrent: () => api.get('/tenant'),
  update: (tenantData) => api.put('/tenant', sanitizeRequestData(tenantData)),
  getUsers: () => api.get('/users'),
  updateUser: (userId, userData) => {
    if (!userId || !userData) {
      return Promise.reject(new Error('Missing user data'));
    }
    return api.put(`/users/${encodeURIComponent(userId)}`, sanitizeRequestData(userData));
  },
  inviteUser: (inviteData) => api.post('/invitations', sanitizeRequestData(inviteData)),
  getInvitations: () => api.get('/invitations'),
  acceptInvitation: (acceptanceData) => api.post('/invitations/accept', sanitizeRequestData(acceptanceData)),
  deleteUser: (userId) => {
    if (!userId) {
      return Promise.reject(new Error('Missing user ID'));
    }
    return api.delete(`/users/${encodeURIComponent(userId)}`);
  }
};

// Enhanced Agent API calls with input validation
export const agentAPI = {
  getAll: (params = {}) => api.get('/agents', { params: sanitizeRequestData(params) }),
  getById: (id) => {
    if (!id) return Promise.reject(new Error('Missing agent ID'));
    return api.get(`/agents/${encodeURIComponent(id)}`);
  },
  create: (data) => {
    if (!data.name || !data.description) {
      return Promise.reject(new Error('Missing required agent data'));
    }
    return api.post('/agents', sanitizeRequestData(data));
  },
  update: (id, data) => {
    if (!id || !data) return Promise.reject(new Error('Missing agent data'));
    return api.put(`/agents/${encodeURIComponent(id)}`, sanitizeRequestData(data));
  },
  delete: (id) => {
    if (!id) return Promise.reject(new Error('Missing agent ID'));
    return api.delete(`/agents/${encodeURIComponent(id)}`);
  },
  start: (id) => {
    if (!id) return Promise.reject(new Error('Missing agent ID'));
    return api.post(`/agents/${encodeURIComponent(id)}/start`);
  },
  stop: (id) => {
    if (!id) return Promise.reject(new Error('Missing agent ID'));
    return api.post(`/agents/${encodeURIComponent(id)}/stop`);
  },
  getTasks: (id, params = {}) => {
    if (!id) return Promise.reject(new Error('Missing agent ID'));
    return api.get(`/agents/${encodeURIComponent(id)}/tasks`, { params: sanitizeRequestData(params) });
  },
  chat: (id, message) => {
    if (!id || !message) return Promise.reject(new Error('Missing agent ID or message'));
    return api.post(`/agents/${encodeURIComponent(id)}/chat`, { message, agent_id: id });
  },
  getChatHistory: (id, limit = 50) => {
    if (!id) return Promise.reject(new Error('Missing agent ID'));
    return api.get(`/agents/${encodeURIComponent(id)}/chat/history`, { params: { limit } });
  },
  getAvailableForConnection: (id) => {
    if (!id) return Promise.reject(new Error('Missing agent ID'));
    return api.get(`/agents/available/${encodeURIComponent(id)}`);
  },
};

// Enhanced Task API calls with validation
export const taskAPI = {
  getAll: (params = {}) => api.get('/tasks', { params: sanitizeRequestData(params) }),
  getById: (id) => {
    if (!id) return Promise.reject(new Error('Missing task ID'));
    return api.get(`/tasks/${encodeURIComponent(id)}`);
  },
  create: (data) => {
    if (!data.prompt) {
      return Promise.reject(new Error('Missing task prompt'));
    }
    return api.post('/tasks', sanitizeRequestData(data));
  },
  execute: (id) => {
    if (!id) return Promise.reject(new Error('Missing task ID'));
    return api.post(`/tasks/${encodeURIComponent(id)}/execute`);
  },
};

// Security API calls for monitoring and auditing
export const securityAPI = {
  getAuditLogs: (params = {}) => api.get('/security/audit-logs', { params: sanitizeRequestData(params) }),
  getSessionInfo: () => api.get('/security/session'),
  reportSecurity: (incident) => api.post('/security/report', sanitizeRequestData(incident)),
  getSecuritySettings: () => api.get('/security/settings'),
  updateSecuritySettings: (settings) => api.put('/security/settings', sanitizeRequestData(settings)),
};

// Health check with security validation
export const healthAPI = {
  check: () => api.get('/health'),
  detailed: () => api.get('/health/detailed'),
};

// Security: Export secure request helpers
export const secureRequest = {
  get: (url, config = {}) => api.get(url, config),
  post: (url, data, config = {}) => api.post(url, sanitizeRequestData(data), config),
  put: (url, data, config = {}) => api.put(url, sanitizeRequestData(data), config),
  delete: (url, config = {}) => api.delete(url, config),
  patch: (url, data, config = {}) => api.patch(url, sanitizeRequestData(data), config),
};

export default api;