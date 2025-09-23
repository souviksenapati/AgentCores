import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Typography,
  Alert,
  AlertTitle,
  Chip,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  Email as EmailIcon,
  Person as PersonIcon,
  Security as SecurityIcon,
  Send as SendIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { 
  USER_ROLES, 
  PERMISSIONS,
  getRoleDisplayName, 
  getRoleColor,
  ROLE_PERMISSIONS 
} from '../utils/rolePermissions';

const UserInvitation = ({ open, onClose, onInvite }) => {
  const { user, hasUserPermission } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    firstName: '',
    lastName: '',
    role: 'viewer',
    message: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Only allow roles that the current user can assign
  const getAssignableRoles = () => {
    switch (user?.role) {
      case 'owner':
        return Object.values(USER_ROLES).filter(role => role !== 'owner'); // Owner can assign all except owner
      case 'admin':
        return ['manager', 'developer', 'analyst', 'operator', 'viewer', 'guest']; // Admin can't create other admins
      case 'manager':
        return ['developer', 'analyst', 'operator', 'viewer', 'guest']; // Manager can assign below manager level
      default:
        return []; // Others can't invite
    }
  };

  const assignableRoles = getAssignableRoles();

  const handleInputChange = (field) => (event) => {
    setFormData(prev => ({
      ...prev,
      [field]: event.target.value
    }));
    if (error) setError('');
  };

  const handleSubmit = async () => {
    // Validation
    if (!formData.email || !formData.firstName || !formData.lastName) {
      setError('Please fill in all required fields');
      return;
    }

    if (!formData.email.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }

    if (!assignableRoles.includes(formData.role)) {
      setError('You do not have permission to assign this role');
      return;
    }

    setIsLoading(true);
    try {
      // Mock API call - replace with actual API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // In real implementation, this would call the backend API
      const invitationData = {
        ...formData,
        invitedBy: user.email,
        invitedAt: new Date().toISOString(),
        status: 'pending'
      };

      if (onInvite) {
        onInvite(invitationData);
      }

      // Reset form
      setFormData({
        email: '',
        firstName: '',
        lastName: '',
        role: 'viewer',
        message: '',
      });

      onClose();
    } catch (err) {
      setError('Failed to send invitation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const selectedRolePermissions = ROLE_PERMISSIONS[formData.role] || [];

  if (!hasUserPermission(PERMISSIONS.INVITE_USERS)) {
    return null;
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <PersonIcon />
          <Typography variant="h6">Invite New User</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            <AlertTitle>Error</AlertTitle>
            {error}
          </Alert>
        )}

        <Alert severity="info" sx={{ mb: 3 }}>
          <AlertTitle>Invitation Process</AlertTitle>
          The user will receive an email invitation with instructions to set up their account. 
          They'll need to accept the invitation within 7 days.
        </Alert>

        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Box display="flex" flexDirection="column" gap={3}>
              {/* Basic Information */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  User Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Email Address"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange('email')}
                      required
                      InputProps={{
                        startAdornment: <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                      }}
                      helperText="The user will receive an invitation at this email address"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="First Name"
                      value={formData.firstName}
                      onChange={handleInputChange('firstName')}
                      required
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Last Name"
                      value={formData.lastName}
                      onChange={handleInputChange('lastName')}
                      required
                    />
                  </Grid>
                </Grid>
              </Box>

              {/* Role Selection */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  Role Assignment
                </Typography>
                <FormControl fullWidth>
                  <InputLabel>User Role</InputLabel>
                  <Select
                    value={formData.role}
                    label="User Role"
                    onChange={handleInputChange('role')}
                    startAdornment={<SecurityIcon sx={{ mr: 1, color: 'text.secondary' }} />}
                  >
                    {assignableRoles.map((role) => (
                      <MenuItem key={role} value={role}>
                        <Box display="flex" alignItems="center" gap={1} width="100%">
                          <Chip 
                            label={getRoleDisplayName(role)}
                            color={getRoleColor(role)}
                            size="small"
                          />
                          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                            {ROLE_PERMISSIONS[role]?.length || 0} permissions
                          </Typography>
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>

              {/* Optional Message */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  Welcome Message (Optional)
                </Typography>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Personal message to include in the invitation"
                  value={formData.message}
                  onChange={handleInputChange('message')}
                  placeholder="Welcome to our team! Looking forward to working with you..."
                />
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            {/* Role Preview */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Role Preview
                </Typography>
                <Box mb={2}>
                  <Chip 
                    label={getRoleDisplayName(formData.role)}
                    color={getRoleColor(formData.role)}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    This role has access to {selectedRolePermissions.length} permissions
                  </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />

                <Typography variant="subtitle2" gutterBottom>
                  Key Permissions:
                </Typography>
                <List dense>
                  {selectedRolePermissions.slice(0, 8).map((permission) => (
                    <ListItem key={permission} sx={{ py: 0.25 }}>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <SecurityIcon fontSize="small" color="primary" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={permission.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        primaryTypographyProps={{ variant: 'caption' }}
                      />
                    </ListItem>
                  ))}
                  {selectedRolePermissions.length > 8 && (
                    <ListItem>
                      <ListItemText 
                        primary={`... and ${selectedRolePermissions.length - 8} more permissions`}
                        primaryTypographyProps={{ variant: 'caption', color: 'text.secondary' }}
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button 
          onClick={onClose} 
          startIcon={<CloseIcon />}
          disabled={isLoading}
        >
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          variant="contained" 
          startIcon={<SendIcon />}
          disabled={isLoading || !formData.email || !formData.firstName || !formData.lastName}
        >
          {isLoading ? 'Sending Invitation...' : 'Send Invitation'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default UserInvitation;