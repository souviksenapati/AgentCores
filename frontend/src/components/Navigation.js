import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  Chip,
} from '@mui/material';
import { AccountCircle, Business, ExitToApp } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const Navigation = () => {
  const { user, tenant, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  // Hide this top nav when a user is logged in to avoid duplication with AppLayout
  if (user) return null;

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
    navigate('/login');
  };

  const handleProfile = () => {
    navigate('/profile');
    handleClose();
  };

  const handleTenantSettings = () => {
    navigate('/tenant/settings');
    handleClose();
  };

  const handleUserManagement = () => {
    navigate('/tenant/users');
    handleClose();
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography
          variant="h6"
          component={Link}
          to={user ? "/dashboard" : "/"}
          sx={{
            flexGrow: 1,
            textDecoration: 'none',
            color: 'inherit',
            fontWeight: 'bold',
          }}
        >
          AgentCores
        </Typography>

        {tenant && (
          <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
            <Business sx={{ mr: 1, fontSize: '1.2rem' }} />
            <Chip
              label={tenant.name}
              variant="outlined"
              sx={{
                color: 'white',
                borderColor: 'rgba(255, 255, 255, 0.5)',
                fontSize: '0.875rem',
              }}
            />
          </Box>
        )}

        {user ? (
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Button
              onClick={handleMenu}
              color="inherit"
              startIcon={<AccountCircle />}
              sx={{ textTransform: 'none' }}
            >
              {user.full_name || user.email}
            </Button>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem disabled>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {user.email}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Role: {user.role}
                  </Typography>
                </Box>
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleProfile}>
                <AccountCircle sx={{ mr: 1 }} />
                Profile
              </MenuItem>
              {user.role === 'owner' && (
                <>
                  <MenuItem onClick={handleTenantSettings}>
                    <Business sx={{ mr: 1 }} />
                    Organization Settings
                  </MenuItem>
                  <MenuItem onClick={handleUserManagement}>
                    <AccountCircle sx={{ mr: 1 }} />
                    Manage Users
                  </MenuItem>
                </>
              )}
              <Divider />
              <MenuItem onClick={handleLogout}>
                <ExitToApp sx={{ mr: 1 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        ) : (
          <Box>
            <Button color="inherit" component={Link} to="/login">
              Login
            </Button>
            <Button color="inherit" component={Link} to="/create-tenant">
              Get Started
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;