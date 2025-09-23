import React, { useState, useEffect } from 'react';
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
  Alert,
  AlertTitle,
  Divider,
  Avatar,
  Badge,
  Tooltip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  CardActions,
} from '@mui/material';
import { useQuery } from 'react-query';
import {
  SmartToy as SmartToyIcon,
  Assignment as AssignmentIcon,
  PlayArrow as PlayArrowIcon,
  Error as ErrorIcon,
  Group as GroupIcon,
  Dashboard as DashboardIcon,
  TrendingUp as AnalyticsIcon,
  Security as SecurityIcon,
  Notifications as NotificationIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Launch as LaunchIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Timeline as TimelineIcon,
  Storage as StorageIcon,
  MonitorHeart as MonitorIcon,
  Business as BusinessIcon,
  VpnKey as ApiKeyIcon,
  Hub as IntegrationIcon,
  Assessment as ReportIcon,
  Paid as CostIcon,
  History as ActivityIcon,
  Code as DeveloperIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material';

import { agentAPI, taskAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { PERMISSIONS, getRoleDisplayName, getRoleColor } from '../utils/rolePermissions';

const Dashboard = () => {
  const { user, tenant, hasUserPermission } = useAuth();
  const [systemHealth, setSystemHealth] = useState('healthy');
  
  const { data: agentsData, isLoading: agentsLoading } = useQuery(
    'agents',
    () => agentAPI.getAll(),
    {
      enabled: hasUserPermission(PERMISSIONS.VIEW_AGENTS),
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      staleTime: 2 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchInterval: false,
    }
  );

  const { data: tasksData, isLoading: tasksLoading } = useQuery(
    'tasks',
    () => taskAPI.getAll(),
    {
      enabled: hasUserPermission(PERMISSIONS.VIEW_TASKS),
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      staleTime: 2 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchInterval: false,
    }
  );

  // Mock data for demo purposes
  useEffect(() => {
    if (user?.role === 'demo') {
      // Simulate some activity for demo users
      const interval = setInterval(() => {
        setSystemHealth(prev => prev === 'healthy' ? 'warning' : 'healthy');
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [user?.role]);

  if ((agentsLoading && hasUserPermission(PERMISSIONS.VIEW_AGENTS)) || 
      (tasksLoading && hasUserPermission(PERMISSIONS.VIEW_TASKS))) {
    return <LinearProgress />;
  }

  const agents = agentsData?.data?.agents || [];
  const tasks = tasksData?.data?.tasks || [];

  // Enhanced stats with role-based visibility
  const stats = {
    totalAgents: hasUserPermission(PERMISSIONS.VIEW_AGENTS) ? agents.length : 0,
    runningAgents: hasUserPermission(PERMISSIONS.VIEW_AGENTS) ? agents.filter(a => a.status === 'running').length : 0,
    idleAgents: hasUserPermission(PERMISSIONS.VIEW_AGENTS) ? agents.filter(a => a.status === 'idle').length : 0,
    errorAgents: hasUserPermission(PERMISSIONS.VIEW_AGENTS) ? agents.filter(a => a.status === 'error').length : 0,
    totalTasks: hasUserPermission(PERMISSIONS.VIEW_TASKS) ? tasks.length : 0,
    pendingTasks: hasUserPermission(PERMISSIONS.VIEW_TASKS) ? tasks.filter(t => t.status === 'pending').length : 0,
    completedTasks: hasUserPermission(PERMISSIONS.VIEW_TASKS) ? tasks.filter(t => t.status === 'completed').length : 0,
    failedTasks: hasUserPermission(PERMISSIONS.VIEW_TASKS) ? tasks.filter(t => t.status === 'failed').length : 0,
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

  const StatCard = ({ title, value, icon, color = 'primary', subtitle = null, onClick = null }) => (
    <Card sx={{ cursor: onClick ? 'pointer' : 'default' }} onClick={onClick}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h4" component="div" color={color}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box color={`${color}.main`} sx={{ opacity: 0.7 }}>
            {icon}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const QuickActionCard = ({ title, description, icon, href, permission, color = 'primary' }) => {
    if (!hasUserPermission(permission)) return null;
    
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box display="flex" alignItems="flex-start" gap={2}>
            <Avatar sx={{ bgcolor: `${color}.main` }}>
              {icon}
            </Avatar>
            <Box flex={1}>
              <Typography variant="h6" gutterBottom>
                {title}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {description}
              </Typography>
            </Box>
          </Box>
        </CardContent>
        <CardActions>
          <Button 
            size="small" 
            href={href}
            startIcon={<LaunchIcon />}
            color={color}
          >
            Open
          </Button>
        </CardActions>
      </Card>
    );
  };

  const AlertCard = ({ severity, title, children }) => (
    <Alert severity={severity} sx={{ mb: 2 }}>
      <AlertTitle>{title}</AlertTitle>
      {children}
    </Alert>
  );

  // Role-specific welcome messages
  const getWelcomeMessage = () => {
    switch (user?.role) {
      case 'owner':
        return 'Complete control over your organization';
      case 'admin':
        return 'Manage your team and systems';
      case 'manager':
        return 'Oversee projects and team performance';
      case 'developer':
        return 'Build and deploy intelligent agents';
      case 'analyst':
        return 'Analyze data and generate insights';
      case 'operator':
        return 'Monitor and maintain system operations';
      case 'viewer':
        return 'View reports and system status';
      case 'guest':
        return 'Limited access to system overview';
      case 'demo':
        return 'Explore our platform capabilities';
      default:
        return 'Welcome to your dashboard';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header with Role Badge */}
      <Box mb={4}>
        <Box display="flex" alignItems="center" justifyContent="space-between" flexWrap="wrap" gap={2}>
          <Box>
            <Typography variant="h4" gutterBottom>
              Dashboard
            </Typography>
            <Box display="flex" alignItems="center" gap={2} flexWrap="wrap">
              <Typography variant="h6" color="text.secondary">
                Welcome back, {user?.full_name || user?.email}
              </Typography>
              <Chip 
                label={getRoleDisplayName(user?.role)}
                color={getRoleColor(user?.role)}
                variant="outlined"
                size="small"
              />
              {tenant && (
                <Chip 
                  label={`${tenant.subscription_tier} plan`}
                  color={getSubscriptionColor(tenant.subscription_tier)}
                  variant="outlined"
                  size="small"
                />
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {getWelcomeMessage()}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Demo User Alert */}
      {user?.role === 'demo' && (
        <AlertCard severity="info" title="Demo Mode Active">
          You're exploring our platform in demo mode. All data shown is for demonstration purposes only.
          Contact us to learn more about our enterprise features.
        </AlertCard>
      )}

      {/* System Health Alert for Operators and Admins */}
      {(hasUserPermission(PERMISSIONS.VIEW_SYSTEM_HEALTH) || hasUserPermission(PERMISSIONS.MANAGE_MONITORING)) && systemHealth !== 'healthy' && (
        <AlertCard severity="warning" title="System Health Alert">
          Some services are experiencing performance issues. Click here to view detailed system status.
        </AlertCard>
      )}
      
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {hasUserPermission(PERMISSIONS.VIEW_AGENTS) && (
          <>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Total Agents"
                value={stats.totalAgents}
                subtitle={`${stats.runningAgents} running`}
                icon={<SmartToyIcon fontSize="large" />}
                color="primary"
                onClick={() => window.location.href = '/agents'}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Running Agents"
                value={stats.runningAgents}
                subtitle={`${stats.idleAgents} idle, ${stats.errorAgents} errors`}
                icon={<PlayArrowIcon fontSize="large" />}
                color="success"
              />
            </Grid>
          </>
        )}
        
        {hasUserPermission(PERMISSIONS.VIEW_TASKS) && (
          <>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Total Tasks"
                value={stats.totalTasks}
                subtitle={`${stats.pendingTasks} pending`}
                icon={<AssignmentIcon fontSize="large" />}
                color="info"
                onClick={() => window.location.href = '/tasks'}
              />
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Task Success Rate"
                value={stats.totalTasks > 0 ? `${Math.round((stats.completedTasks / stats.totalTasks) * 100)}%` : '0%'}
                subtitle={`${stats.failedTasks} failed`}
                icon={<CheckIcon fontSize="large" />}
                color={stats.failedTasks > 0 ? "warning" : "success"}
              />
            </Grid>
          </>
        )}

        {/* Cost overview for those with cost permissions */}
        {hasUserPermission(PERMISSIONS.VIEW_COSTS) && (
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Monthly Spend"
              value="$234.50"
              subtitle="$45.20 this week"
              icon={<CostIcon fontSize="large" />}
              color="secondary"
              onClick={() => window.location.href = '/costs'}
            />
          </Grid>
        )}

        {/* System health for operators */}
        {hasUserPermission(PERMISSIONS.VIEW_SYSTEM_HEALTH) && (
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="System Health"
              value={systemHealth === 'healthy' ? 'Healthy' : 'Warning'}
              subtitle="All services operational"
              icon={<MonitorIcon fontSize="large" />}
              color={systemHealth === 'healthy' ? 'success' : 'warning'}
              onClick={() => window.location.href = '/monitoring'}
            />
          </Grid>
        )}
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions - Role-based */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <QuickActionCard
                  title="Create Agent"
                  description="Build and deploy new AI agents"
                  icon={<SmartToyIcon />}
                  href="/agents/create"
                  permission={PERMISSIONS.CREATE_AGENTS}
                  color="primary"
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <QuickActionCard
                  title="View Analytics"
                  description="Monitor performance and insights"
                  icon={<AnalyticsIcon />}
                  href="/analytics"
                  permission={PERMISSIONS.VIEW_ANALYTICS}
                  color="secondary"
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <QuickActionCard
                  title="Manage Users"
                  description="Add and manage team members"
                  icon={<GroupIcon />}
                  href="/users"
                  permission={PERMISSIONS.MANAGE_USERS}
                  color="info"
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <QuickActionCard
                  title="API Keys"
                  description="Manage integration credentials"
                  icon={<ApiKeyIcon />}
                  href="/api-keys"
                  permission={PERMISSIONS.VIEW_API_KEYS}
                  color="warning"
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <QuickActionCard
                  title="Security"
                  description="Review security settings"
                  icon={<SecurityIcon />}
                  href="/security"
                  permission={PERMISSIONS.VIEW_SECURITY}
                  color="error"
                />
              </Grid>
              
              <Grid item xs={12} sm={6} md={4}>
                <QuickActionCard
                  title="System Admin"
                  description="Advanced system configuration"
                  icon={<AdminIcon />}
                  href="/system-admin"
                  permission={PERMISSIONS.MANAGE_SYSTEM}
                  color="success"
                />
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Side Panel */}
        <Grid item xs={12} md={4}>
          {/* Recent Activity */}
          {hasUserPermission(PERMISSIONS.VIEW_ACTIVITY) && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Agent deployed successfully"
                    secondary="2 minutes ago"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <InfoIcon color="info" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="New task created"
                    secondary="15 minutes ago"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <WarningIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Performance alert resolved"
                    secondary="1 hour ago"
                  />
                </ListItem>
              </List>
              <Button 
                size="small" 
                href="/activity"
                startIcon={<ActivityIcon />}
              >
                View All Activity
              </Button>
            </Paper>
          )}

          {/* Subscription Info */}
          {tenant && hasUserPermission(PERMISSIONS.VIEW_ORG_SETTINGS) && (
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
                {tenant.subscription_tier === 'free' && hasUserPermission(PERMISSIONS.MANAGE_BILLING) && (
                  <Button
                    variant="contained"
                    size="small"
                    sx={{ mt: 2 }}
                    href="/billing"
                  >
                    Upgrade Plan
                  </Button>
                )}
              </Box>
            </Paper>
          )}

          {/* Organization Settings for Owners */}
          {hasUserPermission(PERMISSIONS.MANAGE_ORG_SETTINGS) && (
            <Paper sx={{ p: 3, mt: 3 }}>
              <Typography variant="h6" gutterBottom>
                Organization
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Button
                  variant="outlined"
                  startIcon={<BusinessIcon />}
                  href="/tenant/settings"
                  fullWidth
                  size="small"
                >
                  Organization Settings
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<GroupIcon />}
                  href="/tenant/users"
                  fullWidth
                  size="small"
                >
                  Manage Users
                </Button>
              </Box>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;