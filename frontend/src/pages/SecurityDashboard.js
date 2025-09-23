import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Shield as ShieldIcon,
  VpnKey as KeyIcon,
  Visibility as VisibilityIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export default function SecurityDashboard() {
  const { user, getSessionInfo, hasUserPermission } = useAuth();
  const [securityData, setSecurityData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    setLoading(true);
    // Simulate API call to get security data
    setTimeout(() => {
      const sessionInfo = getSessionInfo();
      setSecurityData({
        securityScore: 85,
        activeSessions: 12,
        failedLogins: 3,
        suspiciousActivity: 1,
        vulnerabilities: {
          critical: 0,
          high: 1,
          medium: 3,
          low: 5
        },
        recentEvents: [
          { id: 1, type: 'login', user: 'admin@demo.com', timestamp: new Date(), status: 'success' },
          { id: 2, type: 'permission_check', user: 'developer@demo.com', timestamp: new Date(Date.now() - 300000), status: 'success' },
          { id: 3, type: 'failed_login', user: 'unknown@test.com', timestamp: new Date(Date.now() - 600000), status: 'failed' },
          { id: 4, type: 'session_timeout', user: 'viewer@demo.com', timestamp: new Date(Date.now() - 900000), status: 'info' },
        ],
        compliance: {
          dataProtection: 'compliant',
          accessControl: 'compliant',
          auditLogging: 'warning',
          encryption: 'compliant'
        },
        sessionInfo
      });
      setLoading(false);
    }, 1000);
  };

  const getSecurityScoreColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const getEventIcon = (type) => {
    switch (type) {
      case 'login': return <PersonIcon color="success" />;
      case 'failed_login': return <ErrorIcon color="error" />;
      case 'permission_check': return <ShieldIcon color="info" />;
      case 'session_timeout': return <ScheduleIcon color="warning" />;
      default: return <SecurityIcon />;
    }
  };

  const getEventColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'failed': return 'error';
      case 'warning': return 'warning';
      default: return 'info';
    }
  };

  const getComplianceColor = (status) => {
    switch (status) {
      case 'compliant': return 'success';
      case 'warning': return 'warning';
      case 'non-compliant': return 'error';
      default: return 'default';
    }
  };

  if (!hasUserPermission('VIEW_SECURITY')) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          You don't have permission to view the security dashboard.
        </Alert>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Security Dashboard</Typography>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading security information...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <SecurityIcon sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h4">Security Dashboard</Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadSecurityData}
        >
          Refresh
        </Button>
      </Box>

      {/* Security Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Security Score
              </Typography>
              <Typography variant="h3" color={`${getSecurityScoreColor(securityData.securityScore)}.main`}>
                {securityData.securityScore}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={securityData.securityScore}
                color={getSecurityScoreColor(securityData.securityScore)}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Sessions
              </Typography>
              <Typography variant="h3">{securityData.activeSessions}</Typography>
              <Typography variant="body2" color="textSecondary">
                Current active users
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Failed Logins
              </Typography>
              <Typography variant="h3" color="warning.main">{securityData.failedLogins}</Typography>
              <Typography variant="body2" color="textSecondary">
                Last 24 hours
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Suspicious Activity
              </Typography>
              <Typography variant="h3" color={securityData.suspiciousActivity > 0 ? 'error.main' : 'success.main'}>
                {securityData.suspiciousActivity}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Potential threats
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Vulnerabilities */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <WarningIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Vulnerability Status
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon><ErrorIcon color="error" /></ListItemIcon>
                  <ListItemText primary="Critical" secondary={`${securityData.vulnerabilities.critical} issues`} />
                  <Chip label={securityData.vulnerabilities.critical} color="error" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><WarningIcon color="warning" /></ListItemIcon>
                  <ListItemText primary="High" secondary={`${securityData.vulnerabilities.high} issues`} />
                  <Chip label={securityData.vulnerabilities.high} color="warning" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><WarningIcon color="info" /></ListItemIcon>
                  <ListItemText primary="Medium" secondary={`${securityData.vulnerabilities.medium} issues`} />
                  <Chip label={securityData.vulnerabilities.medium} color="info" size="small" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckIcon color="success" /></ListItemIcon>
                  <ListItemText primary="Low" secondary={`${securityData.vulnerabilities.low} issues`} />
                  <Chip label={securityData.vulnerabilities.low} color="success" size="small" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Session Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <KeyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Session Security
              </Typography>
              {securityData.sessionInfo ? (
                <List>
                  <ListItem>
                    <ListItemIcon><PersonIcon /></ListItemIcon>
                    <ListItemText 
                      primary="Current User" 
                      secondary={user?.email || 'Unknown'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><ScheduleIcon /></ListItemIcon>
                    <ListItemText 
                      primary="Session Duration" 
                      secondary={`${Math.floor(securityData.sessionInfo.sessionDuration / 60000)} minutes`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><KeyIcon /></ListItemIcon>
                    <ListItemText 
                      primary="Token Expiry" 
                      secondary={`${Math.floor(securityData.sessionInfo.timeUntilExpiry / 60000)} minutes remaining`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><VisibilityIcon /></ListItemIcon>
                    <ListItemText 
                      primary="Last Activity" 
                      secondary={`${Math.floor((Date.now() - securityData.sessionInfo.lastActivity) / 60000)} minutes ago`} 
                    />
                  </ListItem>
                </List>
              ) : (
                <Typography>No session information available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <ShieldIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Compliance Status
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon><CheckIcon color={getComplianceColor(securityData.compliance.dataProtection)} /></ListItemIcon>
                  <ListItemText primary="Data Protection" />
                  <Chip label={securityData.compliance.dataProtection} color={getComplianceColor(securityData.compliance.dataProtection)} size="small" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckIcon color={getComplianceColor(securityData.compliance.accessControl)} /></ListItemIcon>
                  <ListItemText primary="Access Control" />
                  <Chip label={securityData.compliance.accessControl} color={getComplianceColor(securityData.compliance.accessControl)} size="small" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><WarningIcon color={getComplianceColor(securityData.compliance.auditLogging)} /></ListItemIcon>
                  <ListItemText primary="Audit Logging" />
                  <Chip label={securityData.compliance.auditLogging} color={getComplianceColor(securityData.compliance.auditLogging)} size="small" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><CheckIcon color={getComplianceColor(securityData.compliance.encryption)} /></ListItemIcon>
                  <ListItemText primary="Encryption" />
                  <Chip label={securityData.compliance.encryption} color={getComplianceColor(securityData.compliance.encryption)} size="small" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Security Events */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Security Events
              </Typography>
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Event</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>Time</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {securityData.recentEvents.map((event) => (
                      <TableRow key={event.id}>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            {getEventIcon(event.type)}
                            <Typography variant="body2" sx={{ ml: 1 }}>
                              {event.type.replace('_', ' ')}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{event.user}</TableCell>
                        <TableCell>{event.timestamp.toLocaleTimeString()}</TableCell>
                        <TableCell>
                          <Chip 
                            label={event.status} 
                            color={getEventColor(event.status)} 
                            size="small" 
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}