import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Container,
  Chip,
  Button,
  Paper,
} from '@mui/material';
import { useQuery } from 'react-query';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AssignmentIcon from '@mui/icons-material/Assignment';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ErrorIcon from '@mui/icons-material/Error';
import GroupIcon from '@mui/icons-material/Group';
import DashboardIcon from '@mui/icons-material/Dashboard';

import { agentAPI, taskAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const Dashboard = () => {
  const { user, tenant } = useAuth();
  
  const { data: agentsData, isLoading: agentsLoading } = useQuery(
    'agents',
    () => agentAPI.getAll()
  );

  const { data: tasksData, isLoading: tasksLoading } = useQuery(
    'tasks',
    () => taskAPI.getAll()
  );

  if (agentsLoading || tasksLoading) {
    return <LinearProgress />;
  }

  const agents = agentsData?.data?.agents || [];
  const tasks = tasksData?.data?.tasks || [];

  const stats = {
    totalAgents: agents.length,
    runningAgents: agents.filter(a => a.status === 'running').length,
    idleAgents: agents.filter(a => a.status === 'idle').length,
    errorAgents: agents.filter(a => a.status === 'error').length,
    totalTasks: tasks.length,
  };

  const getSubscriptionColor = (tier) => {
    switch (tier) {
      case 'free': return 'default';
      case 'basic': return 'primary';
      case 'professional': return 'secondary';
      case 'enterprise': return 'success';
      default: return 'default';
    }
  };

  const StatCard = ({ title, value, icon, color = 'primary' }) => (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div">
              {value}
            </Typography>
          </Box>
          <Box color={`${color}.main`}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Typography variant="h6" color="text.secondary">
            Welcome back, {user?.full_name || user?.email}
          </Typography>
          {tenant && (
            <Chip 
              label={`${tenant.subscription_tier} plan`}
              color={getSubscriptionColor(tenant.subscription_tier)}
              variant="outlined"
            />
          )}
        </Box>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Agents"
            value={stats.totalAgents}
            icon={<SmartToyIcon fontSize="large" />}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Running Agents"
            value={stats.runningAgents}
            icon={<PlayArrowIcon fontSize="large" />}
            color="success"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Error Agents"
            value={stats.errorAgents}
            icon={<ErrorIcon fontSize="large" />}
            color="error"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Tasks"
            value={stats.totalTasks}
            icon={<AssignmentIcon fontSize="large" />}
            color="info"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box display="flex" flexDirection="column" gap={2}>
              <Button
                variant="contained"
                startIcon={<SmartToyIcon />}
                href="/agents/create"
                fullWidth
              >
                Create New Agent
              </Button>
              <Button
                variant="outlined"
                startIcon={<AssignmentIcon />}
                href="/tasks"
                fullWidth
              >
                View Tasks
              </Button>
              {user?.role === 'owner' && (
                <>
                  <Button
                    variant="outlined"
                    startIcon={<GroupIcon />}
                    href="/tenant/users"
                    fullWidth
                  >
                    Manage Users
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<DashboardIcon />}
                    href="/tenant/settings"
                    fullWidth
                  >
                    Organization Settings
                  </Button>
                </>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* Subscription Info */}
        <Grid item xs={12} md={6}>
          {tenant && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Subscription
              </Typography>
              <Box>
                <Chip
                  label={`${tenant.subscription_tier} Plan`}
                  color={getSubscriptionColor(tenant.subscription_tier)}
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {tenant.subscription_tier === 'free' && 'Up to 5 agents, 1,000 tasks/month'}
                  {tenant.subscription_tier === 'basic' && 'Up to 25 agents, 10,000 tasks/month'}
                  {tenant.subscription_tier === 'professional' && 'Up to 100 agents, 100,000 tasks/month'}
                  {tenant.subscription_tier === 'enterprise' && 'Unlimited agents and tasks'}
                </Typography>
                {tenant.subscription_tier === 'free' && (
                  <Button
                    variant="contained"
                    size="small"
                    sx={{ mt: 2 }}
                    href="/tenant/billing"
                  >
                    Upgrade Plan
                  </Button>
                )}
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;