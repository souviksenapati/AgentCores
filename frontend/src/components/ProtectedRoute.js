import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { CircularProgress, Box } from '@mui/material';
import { hasPermission } from '../utils/rolePermissions';

const ProtectedRoute = ({ 
  children, 
  requireRole = null, 
  requirePermission = null,
  fallbackPath = '/login'
}) => {
  const { user, loading, isAuthenticated } = useAuth();
  const location = useLocation();
  const [authCheck, setAuthCheck] = useState({
    checking: true,
    verified: false,
    error: null
  });

  useEffect(() => {
    const verifyAuthentication = async () => {
      setAuthCheck({ checking: true, verified: false, error: null });

      try {
        // Wait for auth context to stabilize
        if (loading) {
          return;
        }

        // Check if user is authenticated
        if (!user) {
          setAuthCheck({ 
            checking: false, 
            verified: false, 
            error: 'Authentication required' 
          });
          return;
        }

        // Validate user object completeness
        if (!user.id || !user.email || !user.role) {
          console.warn('Incomplete user data detected:', user);
          setAuthCheck({ 
            checking: false, 
            verified: false, 
            error: 'Incomplete user data' 
          });
          return;
        }

        // Check role requirement
        if (requireRole && user.role !== requireRole) {
          console.warn(`Access denied. Required role: ${requireRole}, user role: ${user.role}`);
          setAuthCheck({ 
            checking: false, 
            verified: false, 
            error: `Access denied. Required role: ${requireRole}` 
          });
          return;
        }

        // Check permission requirement
        if (requirePermission && !hasPermission(user.role, requirePermission)) {
          console.warn(`Access denied. Required permission: ${requirePermission}, user role: ${user.role}`);
          setAuthCheck({ 
            checking: false, 
            verified: false, 
            error: `Access denied. Required permission: ${requirePermission}` 
          });
          return;
        }

        // All checks passed
        setAuthCheck({ 
          checking: false, 
          verified: true, 
          error: null 
        });

      } catch (error) {
        console.error('Authentication verification failed:', error);
        setAuthCheck({ 
          checking: false, 
          verified: false, 
          error: 'Authentication verification failed' 
        });
      }
    };

    verifyAuthentication();
  }, [user, loading, requireRole, requirePermission]);

  // Still checking authentication
  if (loading || authCheck.checking) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        gap={2}
      >
        <CircularProgress />
        <Box>Verifying authentication...</Box>
      </Box>
    );
  }

  // Authentication failed - redirect to login
  if (!authCheck.verified && authCheck.error === 'Authentication required') {
    console.log('ProtectedRoute: Authentication required, redirecting to login');
    return (
      <Navigate 
        to={fallbackPath} 
        state={{ 
          from: location,
          reason: 'auth_required',
          message: 'Please log in to access this page'
        }} 
        replace 
      />
    );
  }

  // Permission/role check failed - show unauthorized
  if (!authCheck.verified && authCheck.error) {
    console.log('ProtectedRoute: Authorization failed:', authCheck.error);
    return (
      <Navigate 
        to="/unauthorized" 
        state={{ 
          from: location,
          reason: 'access_denied',
          message: authCheck.error
        }}
        replace 
      />
    );
  }

  // All checks passed - render protected content
  return children;
};

export default ProtectedRoute;