import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
} from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import SmartToyIcon from '@mui/icons-material/SmartToy';

const Navbar = () => {
  const location = useLocation();
  
  // Debug log to ensure component is loading
  console.log('Navbar component loaded with AgentCores branding');

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/agents', label: 'Agents' },
    { path: '/tasks', label: 'Tasks' },
  ];

  return (
    <AppBar position="static">
      <Toolbar>
        <SmartToyIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AgentCores
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              component={Link}
              to={item.path}
              sx={{
                backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;