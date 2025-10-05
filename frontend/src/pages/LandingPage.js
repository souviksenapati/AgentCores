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
  Avatar,
  Paper,
  Stack,
} from '@mui/material';
import {
  SmartToy,
  AutoFixHigh,
  Security,
  Analytics,
  Group,
  Star,
  Shield,
  CloudQueue,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const LandingPage = () => {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    // Wait for auth context to finish loading before checking authentication
    if (!loading && isAuthenticated()) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, loading, navigate]);

  const integrationCategories = [
    { name: 'CRM', count: '25+', icon: <Group /> },
    { name: 'ATS', count: '15+', icon: <SmartToy /> },
    { name: 'HRIS', count: '20+', icon: <Group /> },
    { name: 'Ticketing', count: '18+', icon: <AutoFixHigh /> },
    { name: 'File Storage', count: '12+', icon: <CloudQueue /> },
    { name: 'Accounting', count: '22+', icon: <Analytics /> },
  ];

  const useCases = [
    {
      title: 'Power AI features with customer data',
      description:
        'Fuel your AI product with customer data from your product integrations',
      categories: ['CRM', 'ATS', 'HRIS', 'TCKT', 'FILE'],
    },
    {
      title: 'Implement auto-provisioning',
      description:
        "Say goodbye to manual CSV uploads. Automatically assign your end users' onboarding and permissions with real-time HR employee data",
      categories: ['HRIS'],
    },
    {
      title: 'Build an internal knowledge base',
      description:
        'Improve employee experiences with an internal document database for seamless information access, powered by file data',
      categories: ['FILE'],
    },
    {
      title: 'Analyze project status',
      description:
        "Improve team collaboration and efficiency by pulling in your customers' ticketing data",
      categories: ['TCKT'],
    },
    {
      title: 'Analyze finances',
      description:
        'Provide better and deeper financial insights to your customers, powered by transaction data',
      categories: ['ACCT'],
    },
    {
      title: 'Reconcile vendor payments',
      description:
        "Automatically sync bills and payments between your product and your customers' accounting platform for more efficient and streamlined reconciliation",
      categories: ['ACCT'],
    },
  ];

  const testimonial = {
    quote:
      "17% of the annual recurring revenue we've closed over the past six months can be directly attributed to the collaboration capabilities that AgentCores powers via its AI agent integrations.",
    author: 'Rebecca Houser',
    title: 'Senior Product Manager, Thoropass',
  };

  const complianceBadges = [
    { name: 'SOC 2 Type II', icon: <Shield /> },
    { name: 'ISO 27001', icon: <Security /> },
    { name: 'HIPAA', icon: <Security /> },
    { name: 'GDPR', icon: <Shield /> },
  ];

  return (
    <Box>
      {/* Top Banner */}
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 1 }}>
        <Container maxWidth="lg">
          <Typography variant="body2" textAlign="center">
            <strong>2026 state of AI integrations:</strong> benchmark your
            integration strategy against 160 B2B SaaS companies |
            <Button color="inherit" sx={{ textDecoration: 'underline', ml: 1 }}>
              Learn more
            </Button>
          </Typography>
        </Container>
      </Box>

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Box textAlign="center" mb={8}>
          <Typography
            variant="h1"
            component="h1"
            sx={{
              fontSize: { xs: '2.5rem', md: '4rem' },
              fontWeight: 800,
              lineHeight: 1.1,
              mb: 3,
            }}
          >
            One API, hundreds of
            <br />
            AI agent integrations
          </Typography>

          <Typography
            variant="h4"
            component="h2"
            sx={{
              fontSize: { xs: '1.2rem', md: '1.5rem' },
              fontWeight: 600,
              mb: 2,
            }}
          >
            Integrate fast. Grow faster.
          </Typography>

          <Typography
            variant="body1"
            color="text.secondary"
            sx={{
              mb: 4,
              maxWidth: 600,
              mx: 'auto',
              fontSize: '1.1rem',
              lineHeight: 1.6,
            }}
          >
            Scale your AI agent integrations and immediately open up new revenue
            streams — all with fewer sprints and support tickets
          </Typography>

          <Button
            variant="contained"
            size="large"
            component={Link}
            to="/create-tenant"
            sx={{
              px: 4,
              py: 2,
              fontSize: '1.1rem',
              fontWeight: 600,
              borderRadius: 2,
              mb: 4,
            }}
          >
            Get a demo
          </Button>

          {/* Integration Categories */}
          <Typography variant="body2" color="text.secondary" mb={2}>
            Trusted to power integrations at cutting-edge AI companies,
            <br />
            leading financial services and firms, and top enterprise SaaS
            providers
          </Typography>

          <Grid container spacing={2} justifyContent="center" sx={{ mt: 2 }}>
            {integrationCategories.map((category, index) => (
              <Grid item key={index}>
                <Chip
                  label={`${category.name} ${category.count}`}
                  variant="outlined"
                  icon={category.icon}
                  sx={{ fontWeight: 500 }}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      </Container>

      {/* Value Proposition Section */}
      <Box sx={{ bgcolor: 'grey.50', py: 8 }}>
        <Container maxWidth="lg">
          <Grid container spacing={6} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography
                variant="h3"
                component="h2"
                gutterBottom
                fontWeight="bold"
              >
                Focus on your core product.
                <br />
                We've got your integrations covered.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                sx={{ bgcolor: 'white', p: 3, borderRadius: 2, boxShadow: 1 }}
              >
                <Typography variant="h6" gutterBottom fontWeight="600">
                  Build once into AgentCores
                </Typography>
                <Typography variant="body2" color="text.secondary" mb={3}>
                  Integrate with our unified APIs or MCP server to read and
                  write data from the platforms your customers use
                </Typography>

                <Typography variant="h6" gutterBottom fontWeight="600">
                  AgentCores maintains hundreds of integrations for you
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Outsource your integration maintenance to the leading AI
                  experts and save countless engineering hours
                </Typography>
              </Box>
            </Grid>
          </Grid>

          <Box textAlign="center" mt={4}>
            <Button variant="outlined" size="large">
              Learn how AgentCores works
            </Button>
          </Box>
        </Container>
      </Box>

      {/* Use Cases Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography
          variant="h3"
          component="h2"
          textAlign="center"
          gutterBottom
          fontWeight="bold"
          mb={6}
        >
          Make customer data work for your AI product
        </Typography>

        <Grid container spacing={4}>
          {useCases.map((useCase, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card sx={{ height: '100%', p: 3, borderRadius: 2 }}>
                <CardContent sx={{ p: 0 }}>
                  <Typography variant="h6" gutterBottom fontWeight="600">
                    {useCase.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {useCase.description}
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap">
                    {useCase.categories.map((category, catIndex) => (
                      <Chip
                        key={catIndex}
                        label={category}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box textAlign="center" mt={4}>
          <Button variant="outlined" size="large">
            View all use cases
          </Button>
        </Box>
      </Container>

      {/* Testimonial Section */}
      <Box sx={{ bgcolor: 'grey.50', py: 8 }}>
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            component="h2"
            textAlign="center"
            gutterBottom
            fontWeight="bold"
            mb={6}
          >
            Why teams win with AgentCores
          </Typography>

          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 4, borderRadius: 2 }}>
                <Typography
                  variant="h6"
                  gutterBottom
                  color="primary.main"
                  fontWeight="600"
                >
                  Product teams choose AgentCores to accelerate the product
                  lifecycle—from launch to adoption
                </Typography>
                <Typography
                  variant="body1"
                  paragraph
                  sx={{ fontSize: '1.1rem', fontStyle: 'italic' }}
                >
                  "{testimonial.quote}"
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    {testimonial.author
                      .split(' ')
                      .map(n => n[0])
                      .join('')}
                  </Avatar>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="600">
                      {testimonial.author}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {testimonial.title}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h6" gutterBottom>
                  Product Engineering Go-to-market
                </Typography>
                <Box display="flex" justifyContent="center" gap={1} mb={2}>
                  {[1, 2, 3, 4, 5].map(star => (
                    <Star key={star} sx={{ color: '#ffd700' }} />
                  ))}
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Rated #1 for AI integrations on G2
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Security Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography
          variant="h3"
          component="h2"
          textAlign="center"
          gutterBottom
          fontWeight="bold"
          mb={2}
        >
          Security and compliance are our foundation
        </Typography>

        <Typography
          variant="body1"
          textAlign="center"
          color="text.secondary"
          paragraph
          sx={{ maxWidth: 800, mx: 'auto', mb: 6 }}
        >
          Designed from the ground up to safeguard your customer data,
          AgentCores adheres to the industry's highest standards of security and
          privacy and is certified in SOC 2 Type II, ISO 27001, HIPAA, and the
          GDPR
        </Typography>

        <Grid container spacing={3} justifyContent="center" mb={6}>
          {complianceBadges.map((badge, index) => (
            <Grid item key={index}>
              <Paper
                sx={{
                  p: 3,
                  textAlign: 'center',
                  borderRadius: '50%',
                  width: 100,
                  height: 100,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: 'primary.main',
                  color: 'white',
                }}
              >
                {badge.icon}
                <Typography variant="caption" fontWeight="600" mt={1}>
                  {badge.name}
                </Typography>
              </Paper>
            </Grid>
          ))}
        </Grid>

        <Box textAlign="center">
          <Button variant="outlined" size="large">
            Security at AgentCores
          </Button>
        </Box>

        <Typography
          variant="h5"
          textAlign="center"
          fontWeight="600"
          mt={6}
          mb={4}
        >
          The leader for AI product integrations
        </Typography>

        <Box textAlign="center">
          <Box display="flex" justifyContent="center" gap={1} mb={2}>
            {[1, 2, 3, 4, 5].map(star => (
              <Star key={star} sx={{ color: '#ffd700', fontSize: 30 }} />
            ))}
          </Box>
          <Typography variant="body1" color="text.secondary">
            Leader in AI Integration Management on G2
          </Typography>
        </Box>
      </Container>

      {/* Final CTA Section */}
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 10 }}>
        <Container maxWidth="md" textAlign="center">
          <Typography
            variant="h3"
            component="h2"
            gutterBottom
            fontWeight="bold"
          >
            Make integrations your competitive advantage
          </Typography>
          <Typography
            variant="h6"
            sx={{ mb: 4, opacity: 0.9, maxWidth: 600, mx: 'auto' }}
          >
            Get in touch to learn how AgentCores can unlock hundreds of
            integrations in days, not years
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
              py: 2,
              fontSize: '1.1rem',
              fontWeight: 600,
              borderRadius: 2,
              '&:hover': {
                bgcolor: 'grey.100',
              },
            }}
          >
            Get a demo
          </Button>
        </Container>
      </Box>

      {/* Footer Links Section */}
      <Box sx={{ bgcolor: 'grey.900', color: 'white', py: 6 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid item xs={12} md={3}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Integrations
              </Typography>
              <Stack spacing={1}>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  CRM integrations
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  ATS integrations
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  HR integrations
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  File storage integrations
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  All integrations
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Platform
              </Typography>
              <Stack spacing={1}>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Why AgentCores
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  How AgentCores works
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Security
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Common models
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Developer tools
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Company
              </Typography>
              <Stack spacing={1}>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  About
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Careers
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Blog
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Press
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Contact
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="h6" gutterBottom fontWeight="600">
                Resources
              </Typography>
              <Stack spacing={1}>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Documentation
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  API Reference
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Support
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Status
                </Button>
                <Button
                  color="inherit"
                  sx={{ justifyContent: 'flex-start', p: 0 }}
                >
                  Community
                </Button>
              </Stack>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;
