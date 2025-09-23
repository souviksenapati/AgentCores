import React, { useState, useEffect } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

const UserManagement = () => {
  const { user } = useAuth();
  const [inviteForm, setInviteForm] = useState({
    email: '',
    role: 'viewer',
  });
  const [invitations, setInvitations] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [deleteDialog, setDeleteDialog] = useState({ open: false, invitation: null });

  const roles = [
    { value: 'admin', label: 'Admin', description: 'Full system access' },
    { value: 'manager', label: 'Manager', description: 'Team and project management' },
    { value: 'developer', label: 'Developer', description: 'Development and deployment' },
    { value: 'analyst', label: 'Analyst', description: 'Data analysis and reporting' },
    { value: 'operator', label: 'Operator', description: 'System operations' },
    { value: 'viewer', label: 'Viewer', description: 'Read-only access' },
  ];

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoadingData(true);
    try {
      const [invitationsResponse, usersResponse] = await Promise.all([
        authAPI.getInvitations(),
        authAPI.getUsers(),
      ]);
      setInvitations(invitationsResponse.data);
      setUsers(usersResponse.data);
    } catch (error) {
      console.error('Error loading data:', error);
      setError('Failed to load user data');
    } finally {
      setLoadingData(false);
    }
  };

  const handleInviteFormChange = (e) => {
    setInviteForm({
      ...inviteForm,
      [e.target.name]: e.target.value,
    });
  };

  const handleSendInvitation = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await authAPI.sendInvitation(inviteForm);
      setSuccess(`Invitation sent to ${inviteForm.email}`);
      setInviteForm({ email: '', role: 'viewer' });
      loadData(); // Refresh invitations list
    } catch (error) {
      console.error('Invitation error:', error);
      setError(
        error.response?.data?.detail || 
        'Failed to send invitation. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteInvitation = async (invitationId) => {
    try {
      await authAPI.deleteInvitation(invitationId);
      setSuccess('Invitation deleted successfully');
      loadData();
      setDeleteDialog({ open: false, invitation: null });
    } catch (error) {
      console.error('Delete invitation error:', error);
      setError('Failed to delete invitation');
    }
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      pending: { color: 'warning', label: 'Pending' },
      accepted: { color: 'success', label: 'Accepted' },
      expired: { color: 'error', label: 'Expired' },
    };
    const config = statusConfig[status] || { color: 'default', label: status };
    return <Chip size="small" color={config.color} label={config.label} />;
  };

  const getRoleChip = (role) => {
    const roleColors = {
      owner: 'primary',
      admin: 'secondary', 
      manager: 'info',
      developer: 'success',
      analyst: 'warning',
      operator: 'error',
      viewer: 'default',
    };
    return (
      <Chip 
        size="small" 
        color={roleColors[role] || 'default'} 
        label={role.charAt(0).toUpperCase() + role.slice(1)}
        variant="outlined"
      />
    );
  };

  // Check if user has permission to manage users (owner or admin)
  const canManageUsers = user?.role === 'owner' || user?.role === 'admin';

  if (!canManageUsers) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="warning">
          You don't have permission to manage users. Only organization owners and admins can invite users.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        User Management
      </Typography>
      
      {/* Invite User Form */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Invite New User
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSendInvitation}>
          <Grid container spacing={2} alignItems="end">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                name="email"
                label="Email Address"
                type="email"
                value={inviteForm.email}
                onChange={handleInviteFormChange}
                required
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  name="role"
                  value={inviteForm.role}
                  onChange={handleInviteFormChange}
                  label="Role"
                >
                  {roles.map((role) => (
                    <MenuItem key={role.value} value={role.value}>
                      <Box>
                        <Typography variant="body1">{role.label}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {role.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                disabled={loading}
                sx={{ height: 56 }}
              >
                {loading ? 'Sending...' : 'Send Invite'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Paper>

      {loadingData ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          {/* Pending Invitations */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Pending Invitations ({invitations.filter(inv => inv.status === 'pending').length})
              </Typography>
              <IconButton onClick={loadData} color="primary">
                <RefreshIcon />
              </IconButton>
            </Box>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Email</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Sent Date</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {invitations.map((invitation) => (
                    <TableRow key={invitation.id}>
                      <TableCell>{invitation.email}</TableCell>
                      <TableCell>{getRoleChip(invitation.role)}</TableCell>
                      <TableCell>{getStatusChip(invitation.status)}</TableCell>
                      <TableCell>
                        {new Date(invitation.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {invitation.status === 'pending' && (
                          <IconButton
                            color="error"
                            onClick={() => setDeleteDialog({ open: true, invitation })}
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                  {invitations.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        No pending invitations
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Active Users */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Active Users ({users.length})
            </Typography>
            
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Last Login</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((userData) => (
                    <TableRow key={userData.id}>
                      <TableCell>{userData.full_name}</TableCell>
                      <TableCell>{userData.email}</TableCell>
                      <TableCell>{getRoleChip(userData.role)}</TableCell>
                      <TableCell>
                        {userData.last_login ? 
                          new Date(userData.last_login).toLocaleDateString() : 
                          'Never'
                        }
                      </TableCell>
                      <TableCell>
                        <Chip 
                          size="small" 
                          color="success" 
                          label="Active"
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, invitation: null })}
      >
        <DialogTitle>Delete Invitation</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the invitation for {deleteDialog.invitation?.email}?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, invitation: null })}>
            Cancel
          </Button>
          <Button 
            onClick={() => handleDeleteInvitation(deleteDialog.invitation?.id)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default UserManagement;