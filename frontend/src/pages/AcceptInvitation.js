import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Grid,
  Chip,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

const AcceptInvitation = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [searchParams] = useSearchParams();
  const [invitationData, setInvitationData] = useState(null);
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  });
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const validateInvitation = async () => {
      const token = searchParams.get('token');
      if (!token) {
        setError('Invalid invitation link - missing token');
        setValidating(false);
        return;
      }

      try {
        const response = await authAPI.validateInvitation(token);
        setInvitationData(response.data);
      } catch (error) {
        setError(
          error.response?.data?.detail || 'Invalid or expired invitation link'
        );
      } finally {
        setValidating(false);
      }
    };

    validateInvitation();
  }, [searchParams]);

  const handleChange = e => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validateForm = () => {
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }
    if (!formData.first_name.trim() || !formData.last_name.trim()) {
      setError('First and last name are required');
      return false;
    }
    return true;
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      const token = searchParams.get('token');
      const acceptData = {
        token,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
      };

      const response = await authAPI.acceptInvitation(acceptData);
      const authData = response.data;

      login(authData);
      navigate('/dashboard');
    } catch (error) {
      console.error('Invitation acceptance error:', error);
      setError(
        error.response?.data?.detail ||
          'Failed to accept invitation. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (validating) {
    return (
      <Container component="main" maxWidth="sm">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <CircularProgress />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Validating invitation...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (!invitationData) {
    return (
      <Container component="main" maxWidth="sm">
        <Box
          sx={{
            marginTop: 8,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <Paper
            elevation={3}
            sx={{
              padding: 4,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              width: '100%',
            }}
          >
            <Typography component="h1" variant="h5" color="error">
              Invalid Invitation
            </Typography>
            {error && (
              <Alert severity="error" sx={{ mt: 2, width: '100%' }}>
                {error}
              </Alert>
            )}
            <Box sx={{ mt: 3 }}>
              <Button
                component={Link}
                to="/login"
                variant="contained"
                color="primary"
              >
                Back to Login
              </Button>
            </Box>
          </Paper>
        </Box>
      </Container>
    );
  }

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            padding: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <Typography component="h1" variant="h4" gutterBottom>
            Accept Invitation
          </Typography>

          <Box sx={{ mt: 2, mb: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="primary">
              {invitationData.organization_name}
            </Typography>
            <Typography variant="body1" sx={{ mt: 1 }}>
              You've been invited to join as:
            </Typography>
            <Chip
              label={invitationData.role}
              color="primary"
              variant="outlined"
              sx={{ mt: 1, textTransform: 'capitalize' }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Email: {invitationData.email}
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2, width: '100%' }}>
              {error}
            </Alert>
          )}

          <Box
            component="form"
            onSubmit={handleSubmit}
            sx={{ mt: 1, width: '100%' }}
          >
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  name="first_name"
                  required
                  fullWidth
                  id="first_name"
                  label="First Name"
                  value={formData.first_name}
                  onChange={handleChange}
                  autoFocus
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  required
                  fullWidth
                  id="last_name"
                  label="Last Name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  value={formData.password}
                  onChange={handleChange}
                  helperText="Password must be at least 8 characters long"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  required
                  fullWidth
                  name="confirmPassword"
                  label="Confirm Password"
                  type="password"
                  id="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
              </Grid>
            </Grid>

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Create Account'}
            </Button>

            <Box sx={{ textAlign: 'center' }}>
              <Button component={Link} to="/login" variant="text" size="small">
                Back to Login
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default AcceptInvitation;
