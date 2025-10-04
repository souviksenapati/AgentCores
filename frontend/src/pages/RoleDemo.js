import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  AlertTitle,
  Button,
  CardHeader,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  AdminPanelSettings as OwnerIcon,
  Security as AdminIcon,
  SupervisorAccount as ManagerIcon,
  Code as DeveloperIcon,
  Analytics as AnalystIcon,
  Settings as OperatorIcon,
  Visibility as ViewerIcon,
  Person as GuestIcon,
  Preview as DemoIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { 
  USER_ROLES, 
  PERMISSIONS,
  ROLE_PERMISSIONS,
  getAccessibleMenuItems, 
  getRoleDisplayName, 
  getRoleColor,
} from '../utils/rolePermissions';

export default function RoleDemo() {
  const { user } = useAuth();
  const [selectedRole, setSelectedRole] = useState(user?.role || 'demo');

  if (!user) return null;

  const roleIcons = {
    [USER_ROLES.OWNER]: <OwnerIcon />,
    [USER_ROLES.ADMIN]: <AdminIcon />,
    [USER_ROLES.MANAGER]: <ManagerIcon />,
    [USER_ROLES.DEVELOPER]: <DeveloperIcon />,
    [USER_ROLES.ANALYST]: <AnalystIcon />,
    [USER_ROLES.OPERATOR]: <OperatorIcon />,
    [USER_ROLES.VIEWER]: <ViewerIcon />,
    [USER_ROLES.GUEST]: <GuestIcon />,
    [USER_ROLES.DEMO]: <DemoIcon />,
  };

  const roleDescriptions = {
    [USER_ROLES.OWNER]: 'Complete control over the organization, including billing, user management, and all system features.',
    [USER_ROLES.ADMIN]: 'Almost full access to manage users, systems, and operations, excluding critical organization settings.',
    [USER_ROLES.MANAGER]: 'Team and project management focus with ability to oversee agents, tasks, and team members.',
    [USER_ROLES.DEVELOPER]: 'Technical focus on building and deploying agents, managing integrations, and development tools.',
    [USER_ROLES.ANALYST]: 'Data analysis and reporting focus with access to analytics, metrics, and business intelligence.',
    [USER_ROLES.OPERATOR]: 'Operations and monitoring focus with system health, maintenance, and performance oversight.',
    [USER_ROLES.VIEWER]: 'Read-only access to most features for reviewing status, reports, and system information.',
    [USER_ROLES.GUEST]: 'Very limited read-only access for external stakeholders or temporary access.',
    [USER_ROLES.DEMO]: 'Demonstration mode showcasing platform capabilities with view-only access to key features.',
  };

  const getPermissionStatus = (role, permission) => {
    const rolePermissions = ROLE_PERMISSIONS[role] || [];
    return rolePermissions.includes(permission);
  };

  const categorizePermissions = () => {
    const categories = {
      'Core Features': [
        PERMISSIONS.VIEW_DASHBOARD,
        PERMISSIONS.VIEW_ANALYTICS,
        PERMISSIONS.VIEW_ADVANCED_ANALYTICS,
      ],
      'Agent Management': [
        PERMISSIONS.VIEW_AGENTS,
        PERMISSIONS.CREATE_AGENTS,
        PERMISSIONS.EDIT_AGENTS,
        PERMISSIONS.DELETE_AGENTS,
      ],
      'Task Management': [
        PERMISSIONS.VIEW_TASKS,
        PERMISSIONS.CREATE_TASKS,
        PERMISSIONS.EDIT_TASKS,
        PERMISSIONS.DELETE_TASKS,
      ],
      'User & Organization': [
        PERMISSIONS.VIEW_USERS,
        PERMISSIONS.MANAGE_USERS,
        PERMISSIONS.INVITE_USERS,
        PERMISSIONS.MANAGE_ROLES,
        PERMISSIONS.VIEW_ORG_SETTINGS,
        PERMISSIONS.MANAGE_ORG_SETTINGS,
      ],
      'Monitoring & Security': [
        PERMISSIONS.VIEW_ACTIVITY,
        PERMISSIONS.VIEW_AUDIT_LOGS,
        PERMISSIONS.VIEW_SECURITY,
        PERMISSIONS.MANAGE_SECURITY,
        PERMISSIONS.VIEW_SYSTEM_HEALTH,
      ],
      'Development': [
        PERMISSIONS.VIEW_INTEGRATIONS,
        PERMISSIONS.MANAGE_INTEGRATIONS,
        PERMISSIONS.VIEW_API_KEYS,
        PERMISSIONS.MANAGE_API_KEYS,
        PERMISSIONS.VIEW_DEBUG_INFO,
      ],
      'Billing & Costs': [
        PERMISSIONS.VIEW_COSTS,
        PERMISSIONS.MANAGE_BILLING,
        PERMISSIONS.VIEW_COST_ANALYTICS,
      ],
    };
    return categories;
  };

  const PermissionIcon = ({ hasPermission }) => (
    hasPermission ? 
      <CheckIcon color="success" fontSize="small" /> : 
      <CancelIcon color="error" fontSize="small" />
  );

  const currentUserMenuItems = getAccessibleMenuItems(user.role);
  const currentUserPermissions = ROLE_PERMISSIONS[user.role] || [];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Role-Based Access Control Demo
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Explore how different user roles access various features of the platform. 
        Each role is designed with specific responsibilities and appropriate permissions.
      </Typography>
      
      {user?.role === 'demo' && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <AlertTitle>Demo Mode Active</AlertTitle>
          You are currently viewing the platform as a Demo user. This page shows you what 
          permissions and access each role would have in a real deployment.
        </Alert>
      )}
      
      <Grid container spacing={3}>
        {/* Current User Info */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              avatar={roleIcons[user.role]}
              title="Your Access Level"
              subheader={getRoleDisplayName(user.role)}
            />
            <CardContent>
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={getRoleDisplayName(user.role)}
                  color={getRoleColor(user.role)}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  You have access to {currentUserMenuItems.length} menu items
                  and {currentUserPermissions.length} permissions.
                </Typography>
              </Box>
              
              <Typography variant="subtitle2" gutterBottom>
                Your Available Features:
              </Typography>
              <List dense>
                {currentUserMenuItems.slice(0, 10).map((item) => (
                  <ListItem key={item.id} sx={{ py: 0.25 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      {item.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.label}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
                {currentUserMenuItems.length > 10 && (
                  <ListItem>
                    <ListItemText 
                      primary={`... and ${currentUserMenuItems.length - 10} more`}
                      primaryTypographyProps={{ variant: 'caption', color: 'text.secondary' }}
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Role Selection & Details */}
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Compare Different Roles
              </Typography>
              <Grid container spacing={1}>
                {Object.values(USER_ROLES).map((role) => (
                  <Grid item xs={6} sm={4} md={3} key={role}>
                    <Card 
                      sx={{ 
                        cursor: 'pointer',
                        border: selectedRole === role ? 2 : 1,
                        borderColor: selectedRole === role ? `${getRoleColor(role)}.main` : 'divider',
                        minHeight: 80,
                      }}
                      onClick={() => setSelectedRole(role)}
                    >
                      <CardContent sx={{ textAlign: 'center', py: 1 }}>
                        <Box mb={0.5}>
                          {roleIcons[role]}
                        </Box>
                        <Typography variant="caption" display="block">
                          {getRoleDisplayName(role)}
                        </Typography>
                        <Chip 
                          label={`${ROLE_PERMISSIONS[role]?.length || 0}`}
                          size="small"
                          color={selectedRole === role ? getRoleColor(role) : "default"}
                          variant={selectedRole === role ? "filled" : "outlined"}
                        />
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* Selected Role Details */}
          <Card>
            <CardHeader
              avatar={roleIcons[selectedRole]}
              title={getRoleDisplayName(selectedRole)}
              subheader={roleDescriptions[selectedRole]}
            />
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Permissions by Category
              </Typography>
              
              {Object.entries(categorizePermissions()).map(([category, permissions]) => (
                <Accordion key={category}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={2} width="100%">
                      <Typography variant="subtitle1" sx={{ flex: 1 }}>
                        {category}
                      </Typography>
                      <Chip 
                        label={`${permissions.filter(p => getPermissionStatus(selectedRole, p)).length}/${permissions.length}`}
                        size="small"
                        color={permissions.filter(p => getPermissionStatus(selectedRole, p)).length > 0 ? "primary" : "default"}
                      />
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense>
                      {permissions.map((permission) => (
                        <ListItem key={permission}>
                          <ListItemIcon>
                            <PermissionIcon hasPermission={getPermissionStatus(selectedRole, permission)} />
                          </ListItemIcon>
                          <ListItemText 
                            primary={permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            secondary={permission}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Role Comparison Matrix */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Role Comparison Matrix
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Compare access levels across all roles
              </Typography>
              
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Permission Category</TableCell>
                      {Object.values(USER_ROLES).map((role) => (
                        <TableCell key={role} align="center">
                          <Box display="flex" flexDirection="column" alignItems="center" gap={0.5}>
                            {roleIcons[role]}
                            <Typography variant="caption">
                              {getRoleDisplayName(role)}
                            </Typography>
                          </Box>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(categorizePermissions()).map(([category, permissions]) => (
                      <TableRow key={category}>
                        <TableCell component="th" scope="row">
                          <Typography variant="subtitle2">
                            {category}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {permissions.length} permissions
                          </Typography>
                        </TableCell>
                        {Object.values(USER_ROLES).map((role) => {
                          const hasPermissions = permissions.filter(p => getPermissionStatus(role, p)).length;
                          const percentage = Math.round((hasPermissions / permissions.length) * 100);
                          return (
                            <TableCell key={role} align="center">
                              <Box display="flex" flexDirection="column" alignItems="center" gap={0.5}>
                                <Typography variant="body2">
                                  {hasPermissions}/{permissions.length}
                                </Typography>
                                <Box
                                  sx={{
                                    width: 30,
                                    height: 4,
                                    borderRadius: 2,
                                    backgroundColor: 'grey.300',
                                    position: 'relative',
                                  }}
                                >
                                  <Box
                                    sx={{
                                      width: `${percentage}%`,
                                      height: '100%',
                                      borderRadius: 2,
                                      backgroundColor: `${getRoleColor(role)}.main`,
                                    }}
                                  />
                                </Box>
                              </Box>
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Call to Action */}
        <Grid item xs={12}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" gutterBottom>
                Ready to Get Started?
              </Typography>
              <Typography variant="body1" color="text.secondary" paragraph>
                Contact us to learn more about implementing role-based access control 
                for your organization's specific needs.
              </Typography>
              <Button variant="contained" size="large" href="/support">
                Contact Sales
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}