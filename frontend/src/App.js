import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

import { AuthProvider } from './contexts/AuthContext';
import Navigation from './components/Navigation';
import AppLayout from './components/AppLayout';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import Tasks from './pages/Tasks';
import AgentDetail from './pages/AgentDetail';
import CreateAgent from './pages/CreateAgent';
import Profile from './pages/Profile';
import Unauthorized from './pages/Unauthorized';
import Login from './pages/Login.js';
import Register from './pages/Register';
import CreateTenant from './pages/CreateTenant';
import Placeholder from './pages/Placeholder';
import RoleDemo from './pages/RoleDemo';
import SecurityDashboard from './pages/SecurityDashboard';
import SecurityAudit from './pages/SecurityAudit';
import UserManagement from './pages/UserManagement';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <AuthProvider>
          <Router>
            <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
              {/* Keep top navigation only for public/marketing pages. Authenticated pages will use AppLayout's AppBar. */}
              <Navigation />
              <Box component="main" sx={{ flexGrow: 1 }}>
                <Routes>
                  {/* Public routes */}
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/create-tenant" element={<CreateTenant />} />
                  
                  {/* Protected routes */}
                  <Route path="/dashboard" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <Dashboard />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/agents" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <Agents />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/agents/create" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <CreateAgent />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/agents/:id" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <AgentDetail />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/tasks" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <Tasks />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/profile" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <Profile />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/role-demo" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <RoleDemo />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  {/* Placeholder routes for sidebar entries */}
                  {[
                    '/analytics',
                    '/advanced-analytics', 
                    '/reports',
                    '/costs',
                    '/billing',
                    '/activity',
                    '/monitoring',
                    '/audit-logs',
                    '/system-logs',
                    '/integrations',
                    '/api-keys',
                    '/webhooks',
                    '/debug',
                    '/development',
                    '/compliance',
                    '/tenant/users',
                    '/roles',
                    '/tenant/settings',
                    '/system-admin',
                    '/backups',
                    '/system-config',
                    '/notifications',
                    '/marketplace',
                    '/docs',
                    '/support',
                    '/task-queue',
                  ].map((p) => (
                    <Route key={p} path={p} element={
                      <ProtectedRoute>
                        <AppLayout>
                          <Placeholder title={p.replace('/', '').replace(/-/g, ' ').replace(/\//g, ' / ')} />
                        </AppLayout>
                      </ProtectedRoute>
                    } />
                  ))}
                  {/* Security Dashboard with proper component */}
                  <Route path="/security" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <SecurityDashboard />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/security-audit" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <SecurityAudit />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/users" element={
                    <ProtectedRoute>
                      <AppLayout>
                        <UserManagement />
                      </AppLayout>
                    </ProtectedRoute>
                  } />
                  <Route path="/unauthorized" element={<Unauthorized />} />
                </Routes>
              </Box>
            </Box>
          </Router>
        </AuthProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;