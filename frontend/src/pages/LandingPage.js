import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  SmartToy,
  Dashboard,
  Group,
  Security,
  Speed,
  Cloud,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const LandingPage = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (isAuthenticated()) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);
  const features = [
    {
      icon: <SmartToy sx={{ fontSize: 40 }} />,
      title: 'Intelligent Agents',
      description: 'Create and manage AI-powered agents to automate your workflows',
    },
    {
      icon: <Dashboard sx={{ fontSize: 40 }} />,
      title: 'Comprehensive Dashboard',
      description: 'Monitor and control all your agents from a centralized dashboard',
    },
    {
      icon: <Group sx={{ fontSize: 40 }} />,
      title: 'Team Collaboration',
      description: 'Multi-tenant architecture supporting teams and organizations',
    },
    {
      icon: <Security sx={{ fontSize: 40 }} />,
      title: 'Enterprise Security',
      description: 'Role-based access control and tenant isolation for data security',
    },
    {
      icon: <Speed sx={{ fontSize: 40 }} />,
      title: 'High Performance',
      description: 'Fast and scalable infrastructure built for production workloads',
    },
    {
      icon: <Cloud sx={{ fontSize: 40 }} />,
      title: 'Cloud Native',
      description: 'Docker-based deployment with modern cloud architecture',
    },
  ];

  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      features: ['5 agents', '1,000 tasks/month', 'Basic support', 'Community access'],
      color: 'default',
    },
    {
      name: 'Basic',
      price: '$29',
      period: 'month',
      features: ['25 agents', '10,000 tasks/month', 'Email support', 'Team collaboration'],
      color: 'primary',
    },
    {
      name: 'Professional',
      price: '$99',
      period: 'month',
      features: ['100 agents', '100,000 tasks/month', 'Priority support', 'Advanced analytics'],
      color: 'secondary',
    },
    {
      name: 'Enterprise',
      price: 'Custom',
      period: '',
      features: ['Unlimited agents', 'Unlimited tasks', '24/7 support', 'Custom integrations'],
      color: 'success',
    },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Box textAlign="center" mb={8}>
          <Typography variant="h2" component="h1" gutterBottom fontWeight="bold">
            AgentCores
          </Typography>
          <Typography variant="h5" color="text.secondary" paragraph>
            The next-generation platform for intelligent AI agent management
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
            Build, deploy, and manage AI agents with enterprise-grade security and scalability. 
            Perfect for teams and organizations looking to automate complex workflows.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              size="large"
              component={Link}
              to="/create-tenant"
              sx={{ px: 4, py: 1.5 }}
            >
              Get Started Free
            </Button>
            <Button
              variant="outlined"
              size="large"
              component={Link}
              to="/login"
              sx={{ px: 4, py: 1.5 }}
            >
              Sign In
            </Button>
          </Box>
        </Box>

        {/* Features Section */}
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom sx={{ mb: 6 }}>
          Features
        </Typography>
        <Grid container spacing={4} sx={{ mb: 8 }}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card sx={{ height: '100%', textAlign: 'center', p: 2 }}>
                <CardContent>
                  <Box color="primary.main" sx={{ mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h6" component="h3" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Pricing Section */}
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom sx={{ mb: 6 }}>
          Pricing Plans
        </Typography>
        <Grid container spacing={4} justifyContent="center">
          {plans.map((plan, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  textAlign: 'center', 
                  p: 3,
                  border: plan.name === 'Basic' ? 2 : 1,
                  borderColor: plan.name === 'Basic' ? 'primary.main' : 'divider',
                }}
              >
                <CardContent>
                  <Chip
                    label={plan.name}
                    color={plan.color}
                    sx={{ mb: 2 }}
                  />
                  <Typography variant="h4" component="div" gutterBottom>
                    {plan.price}
                    {plan.period && (
                      <Typography variant="caption" component="span" color="text.secondary">
                        /{plan.period}
                      </Typography>
                    )}
                  </Typography>
                  <Box sx={{ mb: 3 }}>
                    {plan.features.map((feature, featureIndex) => (
                      <Typography
                        key={featureIndex}
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: 1 }}
                      >
                        ✓ {feature}
                      </Typography>
                    ))}
                  </Box>
                  <Button
                    variant={plan.name === 'Basic' ? 'contained' : 'outlined'}
                    fullWidth
                    component={Link}
                    to="/create-tenant"
                    state={{ plan: plan.name.toLowerCase() }}
                  >
                    {plan.name === 'Enterprise' ? 'Contact Sales' : 'Get Started'}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 8 }}>
        <Container maxWidth="md" textAlign="center">
          <Typography variant="h4" component="h2" gutterBottom>
            Ready to Transform Your Workflow?
          </Typography>
          <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
            Join thousands of teams already using AgentCores to automate their processes
          </Typography>
          <Button
            variant="contained"
            size="large"
            component={Link}
            to="/create-tenant"
            sx={{ 
              bgcolor: 'white', 
              color: 'primary.main',
              px: 4,
              py: 1.5,
              '&:hover': {
                bgcolor: 'grey.100',
              }
            }}
          >
            Start Your Free Trial
          </Button>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;