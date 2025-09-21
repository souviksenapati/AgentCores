import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [token, setToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load auth data from localStorage on component mount
  useEffect(() => {
    const loadAuthData = () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        const storedRefreshToken = localStorage.getItem('refresh_token');
        const storedUser = localStorage.getItem('user_data');
        const storedTenant = localStorage.getItem('tenant_data');

        if (storedToken && storedUser && storedTenant) {
          setToken(storedToken);
          setRefreshToken(storedRefreshToken);
          setUser(JSON.parse(storedUser));
          setTenant(JSON.parse(storedTenant));
        }
      } catch (error) {
        console.error('Error loading auth data:', error);
        // Clear corrupted data
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        localStorage.removeItem('tenant_data');
      } finally {
        setLoading(false);
      }
    };

    loadAuthData();
  }, []);

  const login = (authData) => {
    const { access_token, refresh_token, user: userData, tenant: tenantData } = authData;
    
    setToken(access_token);
    setRefreshToken(refresh_token);
    setUser(userData);
    setTenant(tenantData);

    // Store in localStorage
    localStorage.setItem('auth_token', access_token);
    if (refresh_token) {
      localStorage.setItem('refresh_token', refresh_token);
    }
    localStorage.setItem('user_data', JSON.stringify(userData));
    localStorage.setItem('tenant_data', JSON.stringify(tenantData));
  };

  const logout = () => {
    setToken(null);
    setRefreshToken(null);
    setUser(null);
    setTenant(null);

    // Clear localStorage
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
    localStorage.removeItem('tenant_data');
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user_data', JSON.stringify(userData));
  };

  const updateTenant = (tenantData) => {
    setTenant(tenantData);
    localStorage.setItem('tenant_data', JSON.stringify(tenantData));
  };

  const isAuthenticated = () => {
    return !!token && !!user && !!tenant;
  };

  const hasRole = (role) => {
    return user?.role === role;
  };

  const isAdmin = () => {
    return hasRole('admin');
  };

  const isMember = () => {
    return hasRole('member') || hasRole('admin');
  };

  const getTenantSubdomain = () => {
    return tenant?.subdomain;
  };

  const value = {
    user,
    tenant,
    token,
    refreshToken,
    loading,
    login,
    logout,
    updateUser,
    updateTenant,
    isAuthenticated,
    hasRole,
    isAdmin,
    isMember,
    getTenantSubdomain,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;