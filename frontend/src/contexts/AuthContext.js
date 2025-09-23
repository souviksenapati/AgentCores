import React, { createContext, useContext, useState, useEffect } from 'react';
import { hasPermission, ROLE_PERMISSIONS } from '../utils/rolePermissions';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Security constants
const TOKEN_EXPIRY_BUFFER = 5 * 60 * 1000; // 5 minutes buffer before expiry
const MAX_SESSION_TIME = 8 * 60 * 60 * 1000; // 8 hours max session
const ACTIVITY_CHECK_INTERVAL = 60 * 1000; // Check activity every minute

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [token, setToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tokenExpiryTime, setTokenExpiryTime] = useState(null);
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [lastActivity, setLastActivity] = useState(Date.now());

  // Security: Auto-logout on token expiry
  useEffect(() => {
    // TEMPORARILY DISABLED for debugging login issues
    // if (!tokenExpiryTime || !sessionStartTime) return;

    // const checkTokenExpiry = () => {
    //   const now = Date.now();
    //   const timeUntilExpiry = tokenExpiryTime - now;
    //   const sessionDuration = now - sessionStartTime;

    //   // Auto-logout if token expired or max session time reached
    //   if (timeUntilExpiry <= 0 || sessionDuration >= MAX_SESSION_TIME) {
    //     console.warn('Session expired - logging out');
    //     logout();
    //     return;
    //   }

    //   // Warn user before token expires
    //   if (timeUntilExpiry <= TOKEN_EXPIRY_BUFFER && timeUntilExpiry > 0) {
    //     console.warn('Token expiring soon - should refresh');
    //     // Could trigger refresh token flow here
    //   }
    // };

    // const interval = setInterval(checkTokenExpiry, 30000); // Check every 30 seconds
    // return () => clearInterval(interval);
  }, [tokenExpiryTime, sessionStartTime]);

  // Security: Track user activity for idle timeout
  useEffect(() => {
    // TEMPORARILY DISABLED for debugging login issues
    // const updateActivity = () => setLastActivity(Date.now());
    
    // // Track various user interactions
    // const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    // events.forEach(event => {
    //   document.addEventListener(event, updateActivity, true);
    // });

    // // Check for idle timeout
    // const idleCheck = setInterval(() => {
    //   const idleTime = Date.now() - lastActivity;
    //   const maxIdleTime = 30 * 60 * 1000; // 30 minutes idle timeout
      
    //   if (user && idleTime > maxIdleTime) {
    //     console.warn('Session idle timeout - logging out');
    //     logout();
    //   }
    // }, ACTIVITY_CHECK_INTERVAL);

    // return () => {
    //   events.forEach(event => {
    //     document.removeEventListener(event, updateActivity, true);
    //   });
    //   clearInterval(idleCheck);
    // };
  }, [user, lastActivity]);

  // Security: Clear session data when browser/tab is closed or navigated away
  useEffect(() => {
    // TEMPORARILY DISABLED for debugging login issues
    // const handleBeforeUnload = (event) => {
    //   clearStoredAuth();
    // };

    // const handleVisibilityChange = () => {
    //   if (document.hidden && user) {
    //     setTimeout(() => {
    //       if (document.hidden) {
    //         console.warn('Browser/tab closed or hidden - clearing session for security');
    //         clearStoredAuth();
    //         logout();
    //       }
    //     }, 30000);
    //   }
    // };

    // window.addEventListener('beforeunload', handleBeforeUnload);
    // document.addEventListener('visibilitychange', handleVisibilityChange);

    // return () => {
    //   window.removeEventListener('beforeunload', handleBeforeUnload);
    //   document.removeEventListener('visibilitychange', handleVisibilityChange);
    // };
  }, [user]);

  // Security: Validate stored auth data integrity
  const validateStoredAuth = () => {
    try {
      const storedToken = sessionStorage.getItem('auth_token');
      const storedUser = sessionStorage.getItem('user_data');
      const storedTenant = sessionStorage.getItem('tenant_data');
      const storedExpiry = sessionStorage.getItem('token_expiry');
      const storedSessionStart = sessionStorage.getItem('session_start');

      // Check if all required data exists
      if (!storedToken || !storedUser || !storedTenant) {
        return null;
      }

      // Parse and validate JSON data
      let userData, tenantData;
      try {
        userData = JSON.parse(storedUser);
        tenantData = JSON.parse(storedTenant);
      } catch (e) {
        console.error('Invalid JSON in stored auth data');
        return null;
      }

      // Validate required fields
      if (!userData.id || !userData.email || !userData.role || !tenantData.id || !tenantData.name) {
        console.error('Missing required fields in stored auth data');
        return null;
      }

      // Check token expiry
      const expiryTime = parseInt(storedExpiry);
      const sessionStart = parseInt(storedSessionStart);
      const now = Date.now();

      if (expiryTime && now >= expiryTime) {
        console.warn('Stored token has expired');
        return null;
      }

      if (sessionStart && (now - sessionStart) >= MAX_SESSION_TIME) {
        console.warn('Max session time exceeded');
        return null;
      }

      return {
        token: storedToken,
        user: userData,
        tenant: tenantData,
        expiry: expiryTime,
        sessionStart: sessionStart
      };
    } catch (error) {
      console.error('Error validating stored auth data:', error);
      return null;
    }
  };

  // Load auth data from localStorage on component mount
  useEffect(() => {
    const loadAuthData = () => {
      try {
        console.log('🔍 AuthContext: Loading auth data...');
        const validatedAuth = validateStoredAuth();
        
        if (validatedAuth) {
          console.log('✅ AuthContext: Valid auth data found, setting user state');
          setToken(validatedAuth.token);
          setUser(validatedAuth.user);
          setTenant(validatedAuth.tenant);
          setTokenExpiryTime(validatedAuth.expiry);
          setSessionStartTime(validatedAuth.sessionStart);
          
          // Load refresh token separately (may not exist)
          const storedRefreshToken = sessionStorage.getItem('refresh_token');
          if (storedRefreshToken) {
            setRefreshToken(storedRefreshToken);
          }
        } else {
          console.log('❌ AuthContext: No valid auth data found, clearing storage');
          // Clear any corrupted/invalid data
          clearStoredAuth();
        }
      } catch (error) {
        console.error('💥 AuthContext: Error loading auth data:', error);
        clearStoredAuth();
      } finally {
        console.log('🏁 AuthContext: Loading complete, setting loading=false');
        setLoading(false);
      }
    };

    loadAuthData();
  }, []);

  const clearStoredAuth = () => {
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user_data');
    sessionStorage.removeItem('tenant_data');
    sessionStorage.removeItem('token_expiry');
    sessionStorage.removeItem('session_start');
  };

  const login = async (authData) => {
    try {
      const { access_token, refresh_token, user: userData, tenant: tenantData, expires_in } = authData;
      
      // Validate required auth data
      if (!access_token || !userData || !tenantData) {
        throw new Error('Invalid authentication data received');
      }

      // Calculate token expiry time
      const now = Date.now();
      const expiryTime = now + ((expires_in || 3600) * 1000); // Default to 1 hour if not provided
      
      setToken(access_token);
      setRefreshToken(refresh_token);
      setUser(userData);
      setTenant(tenantData);
      setTokenExpiryTime(expiryTime);
      setSessionStartTime(now);
      setLastActivity(now);

      // Store securely in sessionStorage (clears when browser closes)
      sessionStorage.setItem('auth_token', access_token);
      sessionStorage.setItem('user_data', JSON.stringify(userData));
      sessionStorage.setItem('tenant_data', JSON.stringify(tenantData));
      sessionStorage.setItem('token_expiry', expiryTime.toString());
      sessionStorage.setItem('session_start', now.toString());
      
      if (refresh_token) {
        sessionStorage.setItem('refresh_token', refresh_token);
      }

      console.log(`User ${userData.email} logged in successfully with role: ${userData.role}`);
      
      // Wait a brief moment for state to update
      await new Promise(resolve => setTimeout(resolve, 50));
    } catch (error) {
      console.error('Login failed:', error);
      logout(); // Clear any partial state
      throw error;
    }
  };

  const logout = () => {
    try {
      setToken(null);
      setRefreshToken(null);
      setUser(null);
      setTenant(null);
      setTokenExpiryTime(null);
      setSessionStartTime(null);
      setLastActivity(Date.now());

      // Clear all stored data
      clearStoredAuth();

      console.log('User logged out successfully');
    } catch (error) {
      console.error('Logout error:', error);
      // Force clear even if there's an error
      clearStoredAuth();
    }
  };

  const updateUser = (userData) => {
    try {
      if (!userData || !userData.id) {
        throw new Error('Invalid user data');
      }
      
      setUser(userData);
      sessionStorage.setItem('user_data', JSON.stringify(userData));
      console.log('User data updated');
    } catch (error) {
      console.error('Failed to update user data:', error);
    }
  };

  const updateTenant = (tenantData) => {
    try {
      if (!tenantData || !tenantData.id) {
        throw new Error('Invalid tenant data');
      }
      
      setTenant(tenantData);
      sessionStorage.setItem('tenant_data', JSON.stringify(tenantData));
      console.log('Tenant data updated');
    } catch (error) {
      console.error('Failed to update tenant data:', error);
    }
  };

  const isAuthenticated = () => {
    if (!token || !user || !tenant) return false;
    
    // Check if session is still valid
    const now = Date.now();
    if (tokenExpiryTime && now >= tokenExpiryTime) {
      console.warn('Token expired, logging out');
      logout();
      return false;
    }
    if (sessionStartTime && (now - sessionStartTime) >= MAX_SESSION_TIME) {
      console.warn('Max session time exceeded, logging out');
      logout();
      return false;
    }
    
    // Validate user object completeness
    if (!user.id || !user.email || !user.role) {
      console.warn('Incomplete user data, logging out');
      logout();
      return false;
    }
    
    return true;
  };

  const getCurrentUser = async () => {
    if (!isAuthenticated()) {
      throw new Error('Not authenticated');
    }
    
    try {
      // Validate current session with backend
      const response = await authAPI.getCurrentUser();
      return response.data;
    } catch (error) {
      console.error('Failed to get current user:', error);
      if (error.response?.status === 401) {
        logout();
      }
      throw error;
    }
  };

  const hasRole = (role) => {
    return user?.role === role;
  };

  const isAdmin = () => {
    return hasRole('admin') || hasRole('owner');
  };

  const isMember = () => {
    return hasRole('member') || hasRole('admin') || hasRole('owner');
  };

  const getTenantSubdomain = () => {
    return tenant?.subdomain;
  };

  // Security: Permission checking with proper validation
  const hasUserPermission = (permission) => {
    if (!user?.role) return false;
    return hasPermission(user.role, permission);
  };

  const getUserPermissions = () => {
    if (!user?.role) return [];
    return ROLE_PERMISSIONS[user.role] || [];
  };

  // Security: Get session info for monitoring
  const getSessionInfo = () => {
    if (!isAuthenticated()) return null;
    
    const now = Date.now();
    return {
      sessionDuration: sessionStartTime ? now - sessionStartTime : 0,
      timeUntilExpiry: tokenExpiryTime ? tokenExpiryTime - now : 0,
      lastActivity: now - lastActivity,
      isNearExpiry: tokenExpiryTime ? (tokenExpiryTime - now) <= TOKEN_EXPIRY_BUFFER : false
    };
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
    hasUserPermission,
    getUserPermissions,
    getSessionInfo,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;