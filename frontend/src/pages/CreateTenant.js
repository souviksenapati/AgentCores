import React, { useState } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { tenantAPI } from '../services/api';

const CreateTenant = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    contact_email: '',
    contact_name: '',
    subscription_tier: 'free',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const validateName = (name) => {
    // Organization name should be at least 2 characters
    return name.length >= 2;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validate organization name
    if (!validateName(formData.name)) {
      setError('Organization name must be at least 2 characters long');
      setLoading(false);
      return;
    }

    try {
      await tenantAPI.create(formData);
      setSuccess(true);
      
      // Redirect to registration after a short delay
      setTimeout(() => {
        navigate('/register', { 
          state: { tenant_name: formData.name } 
        });
      }, 2000);
    } catch (error) {
      console.error('Tenant creation error:', error);
      setError(
        error.response?.data?.detail || 
        'Failed to create organization. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (success) {
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
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Organization Created Successfully!
              </Typography>
              <Typography variant="body2">
                Your organization "{formData.name}" has been created successfully.
                Redirecting you to create your admin account...
              </Typography>
            </Alert>
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
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Create Organization
          </Typography>
          
          <Typography variant="body2" align="center" color="text.secondary" sx={{ mb: 3 }}>
            Start your AgentCores journey by creating your organization
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="name"
              label="Organization Name"
              name="name"
              autoComplete="organization"
              autoFocus
              value={formData.name}
              onChange={handleChange}
              helperText="The name of your organization (e.g., 'Acme Corporation')"
            />

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
              helperText="Primary contact person for this organization"
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
              helperText="Primary contact email for this organization"
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
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Create Organization'}
            </Button>

            <Box textAlign="center">
              <Typography variant="body2">
                Already have an organization?{' '}
                <Link to="/login" style={{ textDecoration: 'none' }}>
                  Sign In
                </Link>
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default CreateTenant;