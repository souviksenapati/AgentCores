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
  Grid,
  Divider,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Business, Person } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

const Register = () => {
  const navigate = useNavigate();
  const { login, user } = useAuth();
  const [formData, setFormData] = useState({
    organization_name: '',
    contact_name: '',
    contact_email: '',
    subscription_tier: 'free',
    password: '',
    confirmPassword: '',
    userType: 'organization', // 'organization' or 'individual'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [registrationComplete, setRegistrationComplete] = useState(false);

  // Effect to handle navigation after successful registration and login
  useEffect(() => {
    if (registrationComplete && user && (user.role === 'owner' || user.role === 'individual')) {
      console.log('Registration complete and user authenticated, navigating to dashboard');
      navigate('/dashboard');
    }
  }, [registrationComplete, user, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validateForm = () => {
    if (!formData.contact_name || !formData.contact_email || !formData.password) {
      setError('Please fill in all required fields');
      return false;
    }

    // Validate organization name only for organization accounts
    if (formData.userType === 'organization' && !formData.organization_name) {
      setError('Organization name is required for organization accounts');
      return false;
    }

    if (formData.userType === 'organization' && formData.organization_name.length < 2) {
      setError('Organization name must be at least 2 characters long');
      return false;
    }

    if (formData.contact_name.length < 2) {
      setError('Contact name must be at least 2 characters long');
      return false;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.contact_email)) {
      setError('Please enter a valid email address');
      return false;
    }

    // Password strength validation
    const hasUpperCase = /[A-Z]/.test(formData.password);
    const hasLowerCase = /[a-z]/.test(formData.password);
    const hasNumbers = /\d/.test(formData.password);
    
    if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
      setError('Password must contain at least one uppercase letter, one lowercase letter, and one number');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Parse contact name into first and last name
      const nameParts = formData.contact_name.trim().split(' ');
      const first_name = nameParts[0] || '';
      const last_name = nameParts.slice(1).join(' ') || '';

      // Prepare registration data based on user type
      const registrationData = {
        email: formData.contact_email,
        password: formData.password,
        first_name: first_name,
        last_name: last_name,
        subscription_tier: formData.subscription_tier,
      };

      if (formData.userType === 'organization') {
        // Register with organization creation (user becomes the owner)
        registrationData.tenant_name = formData.organization_name;
        registrationData.role = 'owner';
        registrationData.is_individual_account = false; // CRITICAL FIX: Set to false for organizations
        registrationData.is_organization_creation = true;
      } else {
        // Register as individual user
        registrationData.tenant_name = `${first_name} ${last_name}'s Workspace`;
        registrationData.role = 'individual';
        registrationData.is_individual_account = true; // Explicitly set to true for individuals
      }

      const response = await authAPI.register(registrationData);
      const authData = response.data;
      
      // Log the user in with the returned auth data
      await login(authData);
      
      // Set registration complete flag - useEffect will handle navigation
      setRegistrationComplete(true);
    } catch (error) {
      console.error('Registration error:', error);
      if (error.response?.data?.detail?.includes('organization already exists')) {
        setError(formData.userType === 'organization' 
          ? 'An organization with this name already exists. Please choose a different name or contact the existing organization owner for an invitation.'
          : 'A workspace with this name already exists. Please choose a different name.');
      } else if (error.response?.data?.detail?.includes('owner already exists')) {
        setError(formData.userType === 'organization'
          ? 'This organization already has an owner. Only one owner is allowed per organization.'
          : 'Registration failed. Please try again.');
      } else {
        setError(
          error.response?.data?.detail || 
          error.response?.data?.error ||
          'Registration failed. Please try again.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

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
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            {formData.userType === 'organization' ? (
              <Business sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            ) : (
              <Person sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            )}
            
            <Typography component="h1" variant="h4" gutterBottom>
              {formData.userType === 'organization' ? 'Create Organization' : 'Create Individual Account'}
            </Typography>
            
            <Chip 
              icon={formData.userType === 'organization' ? <Person /> : <Person />} 
              label={formData.userType === 'organization' ? 'You will become the Organization Owner' : 'Personal workspace for individual use'} 
              color="primary" 
              variant="outlined"
              sx={{ mb: 2 }}
            />
            
            <Typography variant="body2" color="text.secondary">
              {formData.userType === 'organization' 
                ? 'Start your AgentCores journey by creating your organization. As the owner, you\'ll have full administrative privileges and can invite team members with different roles.'
                : 'Create your personal AgentCores workspace. Perfect for individual projects and personal AI agent management.'
              }
            </Typography>
          </Box>

          <Divider sx={{ mb: 3 }} />

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            {/* Account Type Selection */}
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2, fontWeight: 'bold' }}>
              Account Type
            </Typography>
            
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

            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2, fontWeight: 'bold' }}>
              {formData.userType === 'organization' ? 'Organization Details' : 'Account Details'}
            </Typography>
            
            {/* Organization Name - Only for Organization accounts */}
            {formData.userType === 'organization' && (
              <TextField
                margin="normal"
                required
                fullWidth
                id="organization_name"
                label="Organization Name"
                name="organization_name"
                autoComplete="organization"
                autoFocus
                value={formData.organization_name}
                onChange={handleChange}
                helperText="The name of your organization (e.g., 'Acme Corporation')"
              />
            )}

            <TextField
              margin="normal"
              required
              fullWidth
              id="contact_name"
              label="Contact Name"
              name="contact_name"
              autoComplete="name"
              value={formData.contact_name}
              onChange={handleChange}
              helperText="Your full name as the organization owner"
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="contact_email"
              label="Contact Email"
              name="contact_email"
              autoComplete="email"
              type="email"
              value={formData.contact_email}
              onChange={handleChange}
              helperText="This will be your login email address"
            />

            <FormControl fullWidth margin="normal">
              <InputLabel id="subscription-tier-label">Subscription Tier</InputLabel>
              <Select
                labelId="subscription-tier-label"
                id="subscription_tier"
                name="subscription_tier"
                value={formData.subscription_tier}
                label="Subscription Tier"
                onChange={handleChange}
              >
                <MenuItem value="free">Free (5 agents, 1000 tasks/month)</MenuItem>
                <MenuItem value="basic">Basic (25 agents, 10,000 tasks/month)</MenuItem>
                <MenuItem value="professional">Professional (100 agents, 100,000 tasks/month)</MenuItem>
                <MenuItem value="enterprise">Enterprise (Unlimited)</MenuItem>
              </Select>
            </FormControl>

            <Typography variant="subtitle1" gutterBottom sx={{ mt: 3, fontWeight: 'bold' }}>
              Security Settings
            </Typography>
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="new-password"
              value={formData.password}
              onChange={handleChange}
              helperText="Must be at least 8 characters with uppercase, lowercase, and numbers"
            />

            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              id="confirmPassword"
              autoComplete="new-password"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 
                formData.userType === 'organization' ? 'Create Organization & Become Owner' : 'Create Individual Account'}
            </Button>

            <Box textAlign="center">
              <Typography variant="body2">
                Already have an account?{' '}
                <Link to="/login" style={{ textDecoration: 'none' }}>
                  Sign In
                </Link>
              </Typography>
              <Typography variant="body2" sx={{ mt: 1, fontSize: '0.875rem', color: 'text.secondary' }}>
                Note: Only one owner per organization. You can invite employees with different roles after registration.
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register;