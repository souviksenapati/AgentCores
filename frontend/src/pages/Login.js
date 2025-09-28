import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';
import { Business, Person } from '@mui/icons-material';

const Login = () => {
  const navigate = useNavigate();
  const { login, user } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    organization: '',
    userType: 'organization', // 'organization' or 'individual'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [loginSuccess, setLoginSuccess] = useState(false);
  const [attemptCount, setAttemptCount] = useState(0);

  // Enhanced error extraction
  const extractErrorMessage = (error) => {
    // Priority order for error messages
    const errorSources = [
      error?.response?.data?.error,
      error?.response?.data?.detail,
      error?.response?.data?.message,
      error?.message
    ];

    for (const errorSource of errorSources) {
      if (errorSource && typeof errorSource === 'string') {
        return errorSource;
      }
    }

    // Status-specific messages
    if (error?.response?.status === 401) {
      return 'Invalid email or password. Please check your credentials and try again.';
    } else if (error?.response?.status === 403) {
      return 'Account access is restricted. Please contact your administrator.';
    } else if (error?.response?.status === 429) {
      return 'Too many login attempts. Please wait a few minutes and try again.';
    } else if (error?.response?.status >= 500) {
      return 'Server error. Please try again later.';
    } else if (error?.code === 'NETWORK_ERROR' || !error?.response) {
      return 'Network connection error. Please check your internet connection.';
    }

    return 'Login failed. Please try again.';
  };

  // Enhanced credential validation
  const validateCredentials = (credentials) => {
    const errors = [];
    
    if (!credentials.email) {
      errors.push('Email is required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(credentials.email)) {
      errors.push('Please enter a valid email address');
    }
    
    
    if (!credentials.password) {
      errors.push('Password is required');
    } else if (credentials.password.length < 3) {
      errors.push('Password is too short');
    }

    // Only validate organization for organization users
    if (credentials.userType === 'organization') {
      if (!credentials.organization) {
        errors.push('Organization name is required');
      } else if (credentials.organization.length < 2) {
        errors.push('Organization name must be at least 2 characters');
      }
    }
    
    return errors;
  };

  // Redirect to dashboard if already logged in or after successful login
  useEffect(() => {
    if (user && user.role && loginSuccess) {
      console.log('User authenticated, redirecting to dashboard');
      navigate('/dashboard');
    }
  }, [user, loginSuccess, navigate]);

  // Clear error when user starts typing
  useEffect(() => {
    if (error && (formData.email || formData.password || formData.organization || formData.userType)) {
      const timer = setTimeout(() => {
        setError('');
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [formData.email, formData.password, formData.organization, formData.userType, error]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setLoginSuccess(false);
    setAttemptCount(prev => prev + 1);

    try {
      // Client-side validation
      const validationErrors = validateCredentials(formData);
      if (validationErrors.length > 0) {
        setError(validationErrors.join('. '));
        setLoading(false);
        return;
      }

      console.log(`Login attempt #${attemptCount + 1} for:`, formData.email);
      
      // Add is_individual_account to payload for backend
      const loginPayload = {
        ...formData,
        is_individual_account: formData.userType === 'individual',
      };
      const response = await authAPI.login(loginPayload);
      const authData = response?.data ?? response;

      // Validate response structure
      if (!authData?.access_token || !authData?.user || !authData?.tenant) {
        throw new Error('Invalid authentication response from server');
      }

      // Validate user data completeness
      if (!authData.user.id || !authData.user.email || !authData.user.role) {
        throw new Error('Incomplete user data received');
      }

      console.log('Login successful for:', authData.user.email, 'Role:', authData.user.role);
      
      // Persist auth in context
      await login(authData);

      console.log('Auth context updated, setting success flag');
      // Set success flag - useEffect will handle navigation
      setLoginSuccess(true);
    } catch (err) {
      console.error('Login error:', err);
      const message = extractErrorMessage(err);
      setError(message);
      setLoginSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          mt: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" sx={{ mb: 1 }}>
            Sign In to AgentCores
          </Typography>

          <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
            {formData.userType === 'organization' 
              ? 'Enter your credentials to access your organization'
              : 'Enter your credentials to access your personal workspace'
            }
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            {/* User Type Selection */}
            <FormControl fullWidth margin="normal">
              <InputLabel>Account Type</InputLabel>
              <Select
                name="userType"
                value={formData.userType}
                onChange={handleChange}
                label="Account Type"
              >
                <MenuItem value="organization">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Business />
                    <Box>
                      <Typography variant="body1">Organization</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Multi-user workspace with team management
                      </Typography>
                    </Box>
                  </Box>
                </MenuItem>
                <MenuItem value="individual">
                  <Box display="flex" alignItems="center" gap={1}>
                    <Person />
                    <Box>
                      <Typography variant="body1">Individual</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Personal workspace for individual use
                      </Typography>
                    </Box>
                  </Box>
                </MenuItem>
              </Select>
            </FormControl>

            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              autoComplete="email"
              autoFocus
            />          

            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              value={formData.password}
              onChange={handleChange}
              autoComplete="current-password"
            />

            {/* Conditional Organization Field */}
            {formData.userType === 'organization' && (
              <TextField
                margin="normal"
                required
                fullWidth
                id="organization"
                label="Organization Name"
                name="organization"
                value={formData.organization}
                onChange={handleChange}
                helperText="Enter your organization name (e.g., 'AgentCores Demo')"
              />
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              disabled={loading}
              sx={{ mt: 2, mb: 2 }}
            >
              {loading ? (
                <>
                  <CircularProgress size={18} sx={{ mr: 1 }} /> Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>

            <Divider sx={{ my: 2 }} />

            <Box textAlign="center">
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Don’t have an account? Ask your organization admin to invite you,

              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                <strong>Ready to get started?</strong>{' '}
                <Link to="/register" style={{ textDecoration: 'none' }}>
                  Create Account
                </Link>
              </Typography>
              <Button component={Link} to="/forgot-password" variant="text" size="small">
                Forgot Password?
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
