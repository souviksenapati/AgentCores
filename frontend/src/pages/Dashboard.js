import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
} from '@mui/material';
import { useQuery } from 'react-query';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import AssignmentIcon from '@mui/icons-material/Assignment';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ErrorIcon from '@mui/icons-material/Error';

import { agentAPI, taskAPI } from '../services/api';

const Dashboard = () => {
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
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
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

      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Quick Actions
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Welcome to AgentCores! Use the navigation above to manage your agents and tasks.
        </Typography>
      </Box>
    </Box>
  );
};

export default Dashboard;