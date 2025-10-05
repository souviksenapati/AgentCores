import React, { useState } from 'react';
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Avatar,
  Box,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
  ListSubheader,
  Collapse,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
  Menu as MenuIcon,
  ChevronLeft,
  ChevronRight,
  SmartToy,
  AccountCircle,
  ExitToApp,
  Business,
  ExpandLess,
  ExpandMore,
  Settings as SettingsIcon,
  Group,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { Menu, MenuItem, Chip } from '@mui/material';
import {
  getMenuItemsByCategory,
  MENU_CATEGORIES,
  getRoleDisplayName,
  getRoleColor,
} from '../utils/rolePermissions';

const drawerWidth = 240;
const miniWidth = 68;

export default function AppLayout({ children }) {
  const theme = useTheme();
  const isMdUp = useMediaQuery(theme.breakpoints.up('md'));
  const [open, setOpen] = useState(true); // mini-variant toggle on desktop
  const [mobileOpen, setMobileOpen] = useState(false); // drawer toggle on mobile
  const [expandedCategories, setExpandedCategories] = useState({}); // category collapse state
  const location = useLocation();
  const { user, tenant, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);

  // Get role-based menu items
  const menuItemsByCategory = getMenuItemsByCategory(user?.role);
  const sortedCategories = Object.keys(menuItemsByCategory).sort(
    (a, b) =>
      (MENU_CATEGORIES[a]?.order || 999) - (MENU_CATEGORIES[b]?.order || 999)
  );

  const handleDrawerToggle = () => {
    if (isMdUp) setOpen(prev => !prev);
    else setMobileOpen(prev => !prev);
  };

  const handleCategoryToggle = category => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category],
    }));
  };

  const handleUserMenu = event => setAnchorEl(event.currentTarget);
  const handleUserMenuClose = () => setAnchorEl(null);
  const handleLogout = () => {
    logout();
    handleUserMenuClose();
    navigate('/login');
  };

  // Find current page for title
  const allMenuItems = Object.values(menuItemsByCategory).flat();
  const currentMenuItem = allMenuItems.find(
    item =>
      location.pathname === item.to ||
      location.pathname.startsWith(item.to + '/')
  );

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar sx={{ px: 1, minHeight: 64 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            width: '100%',
            justifyContent: open ? 'space-between' : 'center',
          }}
        >
          {open && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SmartToy fontSize="small" />
              <Typography variant="subtitle1" fontWeight={700}>
                AgentCores
              </Typography>
            </Box>
          )}
          <IconButton onClick={handleDrawerToggle} size="small">
            {isMdUp ? (
              open ? (
                <ChevronLeft />
              ) : (
                <ChevronRight />
              )
            ) : (
              <ChevronLeft />
            )}
          </IconButton>
        </Box>
      </Toolbar>
      <Divider />
      {tenant && (
        <Box sx={{ p: open ? 2 : 1 }}>
          {open ? (
            <Box>
              <Chip
                icon={<Business />}
                label={tenant.name}
                variant="outlined"
                sx={{ maxWidth: '100%', mb: 1 }}
              />
              {user?.role && (
                <Chip
                  label={getRoleDisplayName(user.role)}
                  color={getRoleColor(user.role)}
                  size="small"
                  sx={{ maxWidth: '100%' }}
                />
              )}
            </Box>
          ) : (
            <Tooltip
              title={`${tenant.name} - ${getRoleDisplayName(user?.role)}`}
              placement="right"
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                {(tenant.name || 'T').charAt(0).toUpperCase()}
              </Avatar>
            </Tooltip>
          )}
        </Box>
      )}
      <Divider />
      <Box sx={{ flex: 1, overflowY: 'auto' }}>
        <List sx={{ py: 0 }}>
          {sortedCategories.map(category => {
            const categoryItems = menuItemsByCategory[category];
            const categoryConfig = MENU_CATEGORIES[category];
            const isExpanded = expandedCategories[category] !== false; // default expanded
            const showCategoryHeader = open && categoryItems.length > 0;

            return (
              <React.Fragment key={category}>
                {showCategoryHeader && (
                  <ListSubheader
                    sx={{
                      px: 2,
                      py: 1,
                      cursor: 'pointer',
                      '&:hover': { backgroundColor: 'action.hover' },
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                    onClick={() => handleCategoryToggle(category)}
                  >
                    <Typography
                      variant="caption"
                      fontWeight={600}
                      color="text.secondary"
                    >
                      {categoryConfig?.label || category}
                    </Typography>
                    {isExpanded ? (
                      <ExpandLess fontSize="small" />
                    ) : (
                      <ExpandMore fontSize="small" />
                    )}
                  </ListSubheader>
                )}

                <Collapse
                  in={isExpanded || !open}
                  timeout="auto"
                  unmountOnExit={false}
                >
                  {categoryItems.map(item => {
                    const selected =
                      location.pathname === item.to ||
                      location.pathname.startsWith(item.to + '/');
                    const button = (
                      <ListItemButton
                        component={RouterLink}
                        to={item.to}
                        selected={selected}
                        sx={{
                          minHeight: 40,
                          justifyContent: open ? 'initial' : 'center',
                          px: 1.5,
                          ml: open && showCategoryHeader ? 1 : 0, // indent under categories when expanded
                        }}
                      >
                        <ListItemIcon
                          sx={{
                            minWidth: 36,
                            mr: open ? 1.5 : 0,
                            justifyContent: 'center',
                          }}
                        >
                          {item.icon}
                        </ListItemIcon>
                        {open && <ListItemText primary={item.label} />}
                      </ListItemButton>
                    );
                    return (
                      <ListItem
                        key={item.id}
                        disablePadding
                        sx={{ display: 'block' }}
                      >
                        {open ? (
                          button
                        ) : (
                          <Tooltip title={item.label} placement="right">
                            {button}
                          </Tooltip>
                        )}
                      </ListItem>
                    );
                  })}
                </Collapse>
              </React.Fragment>
            );
          })}
        </List>
      </Box>
      <Divider />
      {/* Footer area */}
      <Box
        sx={{
          p: open ? 1.5 : 1,
          display: 'flex',
          justifyContent: open ? 'space-between' : 'center',
          alignItems: 'center',
        }}
      >
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: open ? 'block' : 'none' }}
        >
          v{process.env.REACT_APP_VERSION || '1.0.0'}
        </Typography>
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: open ? 'block' : 'none' }}
        >
          {process.env.REACT_APP_ENVIRONMENT || 'development'}
        </Typography>
      </Box>
    </Box>
  );

  const container =
    typeof window !== 'undefined' ? () => window.document.body : undefined;

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      {/* Top AppBar */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: t => t.zIndex.drawer + 1,
          ml: isMdUp ? (open ? `${drawerWidth}px` : `${miniWidth}px`) : 0,
          width: isMdUp
            ? `calc(100% - ${open ? drawerWidth : miniWidth}px)`
            : '100%',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 1 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
            {currentMenuItem?.label || 'App'}
          </Typography>
          {/* User menu */}
          <IconButton color="inherit" onClick={handleUserMenu} sx={{ p: 0.5 }}>
            {user?.avatar_url ? (
              <Avatar src={user.avatar_url} />
            ) : (
              <Avatar>
                <AccountCircle />
              </Avatar>
            )}
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleUserMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            <MenuItem disabled>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  {user?.email}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Role: {getRoleDisplayName(user?.role)}
                </Typography>
              </Box>
            </MenuItem>
            <Divider />
            <MenuItem
              component={RouterLink}
              to="/profile"
              onClick={handleUserMenuClose}
            >
              <AccountCircle style={{ marginRight: 8 }} /> Profile
            </MenuItem>
            {user?.role === 'owner' && (
              <>
                <MenuItem
                  component={RouterLink}
                  to="/tenant/settings"
                  onClick={handleUserMenuClose}
                >
                  <SettingsIcon style={{ marginRight: 8 }} /> Organization
                  Settings
                </MenuItem>
                <MenuItem
                  component={RouterLink}
                  to="/tenant/users"
                  onClick={handleUserMenuClose}
                >
                  <Group style={{ marginRight: 8 }} /> Manage Users
                </MenuItem>
              </>
            )}
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ExitToApp style={{ marginRight: 8 }} /> Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Side Drawer */}
      <Box
        component="nav"
        sx={{
          width: { md: open ? drawerWidth : miniWidth },
          flexShrink: { md: 0 },
        }}
        aria-label="sidebar navigation"
      >
        {/* Mobile */}
        <Drawer
          container={container}
          variant="temporary"
          open={!isMdUp && mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: drawerWidth,
            },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Desktop */}
        <Drawer
          variant="permanent"
          open={open}
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              position: 'relative',
              whiteSpace: 'nowrap',
              boxSizing: 'border-box',
              width: open ? drawerWidth : miniWidth,
              overflowX: 'hidden',
              transition: t =>
                t.transitions.create('width', {
                  easing: t.transitions.easing.sharp,
                  duration: t.transitions.duration.enteringScreen,
                }),
            },
          }}
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 2,
          mt: 8,
          width: '100%',
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
