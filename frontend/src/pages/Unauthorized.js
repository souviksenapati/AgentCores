import React from 'react';
import { Container, Typography, Button, Box, Alert } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import { Warning } from '@mui/icons-material';

const Unauthorized = () => {
  const location = useLocation();
  const { reason, message, from } = location.state || {};

  const getErrorDetails = () => {
    switch (reason) {
      case 'auth_required':
        return {
          title: 'Login Required',
          description: message || 'Please log in to access this page.',
          action: 'Go to Login',
          actionPath: '/login',
        };
      case 'access_denied':
        return {
          title: 'Access Denied',
          description:
            message || "You don't have permission to access this page.",
          action: 'Go to Dashboard',
          actionPath: '/dashboard',
        };
      default:
        return {
          title: 'Access Denied',
          description:
            "You don't have permission to access this page. Please contact your administrator if you believe this is an error.",
          action: 'Go to Dashboard',
          actionPath: '/dashboard',
        };
    }
  };

  const errorDetails = getErrorDetails();

  return (
    <Container maxWidth="sm" sx={{ mt: 8, textAlign: 'center' }}>
      <Box>
        <Warning sx={{ fontSize: 64, color: 'warning.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom>
          {errorDetails.title}
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          {errorDetails.description}
        </Typography>

        {reason && (
          <Alert severity="warning" sx={{ mb: 3, textAlign: 'left' }}>
            <Typography variant="body2">
              <strong>Reason:</strong>{' '}
              {reason === 'auth_required'
                ? 'Authentication required'
                : 'Insufficient permissions'}
            </Typography>
            {from && (
              <Typography variant="body2">
                <strong>Attempted to access:</strong> {from.pathname}
              </Typography>
            )}
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="contained"
            component={Link}
            to={errorDetails.actionPath}
          >
            {errorDetails.action}
          </Button>

          {from && reason === 'auth_required' && (
            <Button
              variant="outlined"
              component={Link}
              to="/login"
              state={{ from: from }}
            >
              Login to Continue
            </Button>
          )}
        </Box>
      </Box>
    </Container>
  );
};

export default Unauthorized;
