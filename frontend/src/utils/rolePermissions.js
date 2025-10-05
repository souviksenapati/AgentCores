import {
  Dashboard as DashboardIcon,
  SmartToy,
  AddCircleOutline,
  ListAlt,
  Timeline,
  Paid,
  History,
  Hub,
  Group,
  CreditCard,
  VpnKey,
  Gavel,
  Notifications as NotificationsIcon,
  HelpOutline,
  MenuBook,
  Storefront,
  Security,
  Policy,
  BugReport,
  Cloud,
  DataObject,
  Assignment,
  MonitorHeart,
  Build,
  AdminPanelSettings,
  SupervisorAccount,
  Business,
  TrendingUp,
  Assessment,
  Storage,
  Code,
} from '@mui/icons-material';

// Define user roles with hierarchy
export const USER_ROLES = {
  OWNER: 'owner', // Organization owner - full access
  ADMIN: 'admin', // Administrator - almost full access
  MANAGER: 'manager', // Team manager - team and project management
  DEVELOPER: 'developer', // Developer - agent creation and technical features
  ANALYST: 'analyst', // Data analyst - analytics and reporting
  INDIVIDUAL: 'individual', // Individual user - personal workspace
  OPERATOR: 'operator', // Operations - monitoring and maintenance
  VIEWER: 'viewer', // Read-only access to most features
  GUEST: 'guest', // Limited read-only access
  DEMO: 'demo', // Demo mode - showcase features with limited access
};

// Define permissions
export const PERMISSIONS = {
  // Dashboard & Overview
  VIEW_DASHBOARD: 'view_dashboard',
  VIEW_ANALYTICS: 'view_analytics',
  VIEW_ADVANCED_ANALYTICS: 'view_advanced_analytics',

  // Agents Management
  VIEW_AGENTS: 'view_agents',
  CREATE_AGENTS: 'create_agents',
  EDIT_AGENTS: 'edit_agents',
  DELETE_AGENTS: 'delete_agents',
  MANAGE_AGENT_PERMISSIONS: 'manage_agent_permissions',

  // Tasks Management
  VIEW_TASKS: 'view_tasks',
  CREATE_TASKS: 'create_tasks',
  EDIT_TASKS: 'edit_tasks',
  DELETE_TASKS: 'delete_tasks',
  VIEW_TASK_DETAILS: 'view_task_details',

  // Cost & Billing
  VIEW_COSTS: 'view_costs',
  MANAGE_BILLING: 'manage_billing',
  VIEW_COST_ANALYTICS: 'view_cost_analytics',
  SET_COST_LIMITS: 'set_cost_limits',

  // Integrations & APIs
  VIEW_INTEGRATIONS: 'view_integrations',
  MANAGE_INTEGRATIONS: 'manage_integrations',
  VIEW_API_KEYS: 'view_api_keys',
  MANAGE_API_KEYS: 'manage_api_keys',

  // User & Organization Management
  VIEW_USERS: 'view_users',
  MANAGE_USERS: 'manage_users',
  INVITE_USERS: 'invite_users',
  MANAGE_ROLES: 'manage_roles',
  VIEW_ORG_SETTINGS: 'view_org_settings',
  MANAGE_ORG_SETTINGS: 'manage_org_settings',

  // Monitoring & Logs
  VIEW_ACTIVITY: 'view_activity',
  VIEW_AUDIT_LOGS: 'view_audit_logs',
  VIEW_SYSTEM_LOGS: 'view_system_logs',
  MANAGE_MONITORING: 'manage_monitoring',

  // Security & Compliance
  VIEW_SECURITY: 'view_security',
  MANAGE_SECURITY: 'manage_security',
  VIEW_COMPLIANCE: 'view_compliance',
  MANAGE_COMPLIANCE: 'manage_compliance',

  // System Administration
  MANAGE_SYSTEM: 'manage_system',
  VIEW_SYSTEM_HEALTH: 'view_system_health',
  MANAGE_BACKUPS: 'manage_backups',

  // Development & Debugging
  VIEW_DEBUG_INFO: 'view_debug_info',
  MANAGE_DEVELOPMENT: 'manage_development',

  // Support & Documentation
  VIEW_SUPPORT: 'view_support',
  MANAGE_SUPPORT: 'manage_support',
  VIEW_DOCS: 'view_docs',
  MANAGE_DOCS: 'manage_docs',
};

// Role to permissions mapping
export const ROLE_PERMISSIONS = {
  [USER_ROLES.OWNER]: [
    // Full access to everything
    ...Object.values(PERMISSIONS),
  ],

  [USER_ROLES.ADMIN]: [
    // Almost full access, except critical org settings
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.VIEW_ADVANCED_ANALYTICS,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.CREATE_AGENTS,
    PERMISSIONS.EDIT_AGENTS,
    PERMISSIONS.DELETE_AGENTS,
    PERMISSIONS.MANAGE_AGENT_PERMISSIONS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.CREATE_TASKS,
    PERMISSIONS.EDIT_TASKS,
    PERMISSIONS.DELETE_TASKS,
    PERMISSIONS.VIEW_TASK_DETAILS,
    PERMISSIONS.VIEW_COSTS,
    PERMISSIONS.VIEW_COST_ANALYTICS,
    PERMISSIONS.SET_COST_LIMITS,
    PERMISSIONS.VIEW_INTEGRATIONS,
    PERMISSIONS.MANAGE_INTEGRATIONS,
    PERMISSIONS.VIEW_API_KEYS,
    PERMISSIONS.MANAGE_API_KEYS,
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.MANAGE_USERS,
    PERMISSIONS.INVITE_USERS,
    PERMISSIONS.MANAGE_ROLES,
    PERMISSIONS.VIEW_ORG_SETTINGS,
    PERMISSIONS.VIEW_ACTIVITY,
    PERMISSIONS.VIEW_AUDIT_LOGS,
    PERMISSIONS.VIEW_SYSTEM_LOGS,
    PERMISSIONS.MANAGE_MONITORING,
    PERMISSIONS.VIEW_SECURITY,
    PERMISSIONS.MANAGE_SECURITY,
    PERMISSIONS.VIEW_COMPLIANCE,
    PERMISSIONS.VIEW_SYSTEM_HEALTH,
    PERMISSIONS.VIEW_DEBUG_INFO,
    PERMISSIONS.VIEW_SUPPORT,
    PERMISSIONS.MANAGE_SUPPORT,
    PERMISSIONS.VIEW_DOCS,
  ],

  [USER_ROLES.MANAGER]: [
    // Team and project management focus
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.CREATE_AGENTS,
    PERMISSIONS.EDIT_AGENTS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.CREATE_TASKS,
    PERMISSIONS.EDIT_TASKS,
    PERMISSIONS.VIEW_TASK_DETAILS,
    PERMISSIONS.VIEW_COSTS,
    PERMISSIONS.VIEW_COST_ANALYTICS,
    PERMISSIONS.SET_COST_LIMITS,
    PERMISSIONS.VIEW_INTEGRATIONS,
    PERMISSIONS.VIEW_API_KEYS,
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.INVITE_USERS,
    PERMISSIONS.VIEW_ACTIVITY,
    PERMISSIONS.VIEW_AUDIT_LOGS,
    PERMISSIONS.VIEW_SUPPORT,
    PERMISSIONS.VIEW_DOCS,
  ],

  [USER_ROLES.DEVELOPER]: [
    // Technical development focus
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.CREATE_AGENTS,
    PERMISSIONS.EDIT_AGENTS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.CREATE_TASKS,
    PERMISSIONS.EDIT_TASKS,
    PERMISSIONS.VIEW_TASK_DETAILS,
    PERMISSIONS.VIEW_COSTS,
    PERMISSIONS.VIEW_INTEGRATIONS,
    PERMISSIONS.MANAGE_INTEGRATIONS,
    PERMISSIONS.VIEW_API_KEYS,
    PERMISSIONS.MANAGE_API_KEYS,
    PERMISSIONS.VIEW_ACTIVITY,
    PERMISSIONS.VIEW_DEBUG_INFO,
    PERMISSIONS.MANAGE_DEVELOPMENT,
    PERMISSIONS.VIEW_SUPPORT,
    PERMISSIONS.VIEW_DOCS,
  ],

  [USER_ROLES.ANALYST]: [
    // Analytics and reporting focus
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.VIEW_ADVANCED_ANALYTICS,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.VIEW_TASK_DETAILS,
    PERMISSIONS.VIEW_COSTS,
    PERMISSIONS.VIEW_COST_ANALYTICS,
    PERMISSIONS.VIEW_ACTIVITY,
    PERMISSIONS.VIEW_AUDIT_LOGS,
    PERMISSIONS.VIEW_SUPPORT,
    PERMISSIONS.VIEW_DOCS,
  ],

  [USER_ROLES.OPERATOR]: [
    // Operations and monitoring focus
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.VIEW_TASK_DETAILS,
    PERMISSIONS.VIEW_COSTS,
    PERMISSIONS.VIEW_INTEGRATIONS,
    PERMISSIONS.VIEW_ACTIVITY,
    PERMISSIONS.VIEW_AUDIT_LOGS,
    PERMISSIONS.VIEW_SYSTEM_LOGS,
    PERMISSIONS.MANAGE_MONITORING,
    PERMISSIONS.VIEW_SYSTEM_HEALTH,
    PERMISSIONS.VIEW_SUPPORT,
    PERMISSIONS.VIEW_DOCS,
  ],

  [USER_ROLES.VIEWER]: [
    // Read-only access to most features
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.VIEW_TASK_DETAILS,
    PERMISSIONS.VIEW_COSTS,
    PERMISSIONS.VIEW_INTEGRATIONS,
    PERMISSIONS.VIEW_API_KEYS,
    PERMISSIONS.VIEW_ACTIVITY,
    PERMISSIONS.VIEW_SUPPORT,
    PERMISSIONS.VIEW_DOCS,
  ],

  [USER_ROLES.GUEST]: [
    // Very limited read-only access
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.VIEW_DOCS,
  ],

  [USER_ROLES.INDIVIDUAL]: [
    // Individual user - personal workspace without organization features
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.CREATE_AGENTS,
    PERMISSIONS.EDIT_AGENTS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.CREATE_TASKS,
    PERMISSIONS.EDIT_TASKS,
    PERMISSIONS.VIEW_TASK_DETAILS,
    PERMISSIONS.VIEW_COSTS,
    PERMISSIONS.VIEW_INTEGRATIONS,
    PERMISSIONS.MANAGE_INTEGRATIONS,
    PERMISSIONS.VIEW_API_KEYS,
    PERMISSIONS.MANAGE_API_KEYS,
    PERMISSIONS.VIEW_ACTIVITY,
    PERMISSIONS.VIEW_DOCS,
    PERMISSIONS.VIEW_SUPPORT,
  ],

  [USER_ROLES.DEMO]: [
    // Demo mode - showcase all features with view-only access
    PERMISSIONS.VIEW_DASHBOARD,
    PERMISSIONS.VIEW_ANALYTICS,
    PERMISSIONS.VIEW_AGENTS,
    PERMISSIONS.VIEW_TASKS,
    PERMISSIONS.VIEW_TASK_DETAILS,
    PERMISSIONS.VIEW_COSTS,
    PERMISSIONS.VIEW_INTEGRATIONS,
    PERMISSIONS.VIEW_API_KEYS,
    PERMISSIONS.VIEW_ACTIVITY,
    PERMISSIONS.VIEW_USERS,
    PERMISSIONS.VIEW_DOCS,
    PERMISSIONS.VIEW_SUPPORT,
  ],
};

// Navigation menu items with role-based access
export const NAVIGATION_ITEMS = [
  // Core Dashboard
  {
    id: 'dashboard',
    label: 'Dashboard',
    to: '/dashboard',
    icon: <DashboardIcon />,
    permissions: [PERMISSIONS.VIEW_DASHBOARD],
    category: 'core',
  },

  // Agent Management
  {
    id: 'agents',
    label: 'Agents',
    to: '/agents',
    icon: <SmartToy />,
    permissions: [PERMISSIONS.VIEW_AGENTS],
    category: 'agents',
  },
  {
    id: 'create-agent',
    label: 'Create Agent',
    to: '/agents/create',
    icon: <AddCircleOutline />,
    permissions: [PERMISSIONS.CREATE_AGENTS],
    category: 'agents',
  },

  // Task Management
  {
    id: 'tasks',
    label: 'Tasks',
    to: '/tasks',
    icon: <ListAlt />,
    permissions: [PERMISSIONS.VIEW_TASKS],
    category: 'tasks',
  },
  {
    id: 'task-queue',
    label: 'Task Queue',
    to: '/task-queue',
    icon: <Assignment />,
    permissions: [PERMISSIONS.VIEW_TASKS, PERMISSIONS.MANAGE_MONITORING],
    category: 'tasks',
  },

  // Analytics & Reporting
  {
    id: 'analytics',
    label: 'Analytics',
    to: '/analytics',
    icon: <Timeline />,
    permissions: [PERMISSIONS.VIEW_ANALYTICS],
    category: 'analytics',
  },
  {
    id: 'advanced-analytics',
    label: 'Advanced Analytics',
    to: '/advanced-analytics',
    icon: <Assessment />,
    permissions: [PERMISSIONS.VIEW_ADVANCED_ANALYTICS],
    category: 'analytics',
  },
  {
    id: 'reports',
    label: 'Reports',
    to: '/reports',
    icon: <TrendingUp />,
    permissions: [PERMISSIONS.VIEW_ANALYTICS],
    category: 'analytics',
  },

  // Cost Management
  {
    id: 'costs',
    label: 'Costs',
    to: '/costs',
    icon: <Paid />,
    permissions: [PERMISSIONS.VIEW_COSTS],
    category: 'billing',
  },
  {
    id: 'billing',
    label: 'Billing',
    to: '/billing',
    icon: <CreditCard />,
    permissions: [PERMISSIONS.MANAGE_BILLING],
    category: 'billing',
  },

  // Monitoring & Operations
  {
    id: 'activity',
    label: 'Activity',
    to: '/activity',
    icon: <History />,
    permissions: [PERMISSIONS.VIEW_ACTIVITY],
    category: 'monitoring',
  },
  {
    id: 'monitoring',
    label: 'System Health',
    to: '/monitoring',
    icon: <MonitorHeart />,
    permissions: [PERMISSIONS.VIEW_SYSTEM_HEALTH],
    category: 'monitoring',
  },
  {
    id: 'audit-logs',
    label: 'Audit Logs',
    to: '/audit-logs',
    icon: <Gavel />,
    permissions: [PERMISSIONS.VIEW_AUDIT_LOGS],
    category: 'monitoring',
  },
  {
    id: 'system-logs',
    label: 'System Logs',
    to: '/system-logs',
    icon: <Storage />,
    permissions: [PERMISSIONS.VIEW_SYSTEM_LOGS],
    category: 'monitoring',
  },

  // Integrations & APIs
  {
    id: 'integrations',
    label: 'Integrations',
    to: '/integrations',
    icon: <Hub />,
    permissions: [PERMISSIONS.VIEW_INTEGRATIONS],
    category: 'integrations',
  },
  {
    id: 'api-keys',
    label: 'API Keys',
    to: '/api-keys',
    icon: <VpnKey />,
    permissions: [PERMISSIONS.VIEW_API_KEYS],
    category: 'integrations',
  },
  {
    id: 'webhooks',
    label: 'Webhooks',
    to: '/webhooks',
    icon: <DataObject />,
    permissions: [PERMISSIONS.MANAGE_INTEGRATIONS],
    category: 'integrations',
  },

  // Development & Debug
  {
    id: 'debug',
    label: 'Debug Console',
    to: '/debug',
    icon: <BugReport />,
    permissions: [PERMISSIONS.VIEW_DEBUG_INFO],
    category: 'development',
  },
  {
    id: 'development',
    label: 'Developer Tools',
    to: '/development',
    icon: <Code />,
    permissions: [PERMISSIONS.MANAGE_DEVELOPMENT],
    category: 'development',
  },

  // Security & Compliance
  {
    id: 'security',
    label: 'Security',
    to: '/security',
    icon: <Security />,
    permissions: [PERMISSIONS.VIEW_SECURITY],
    category: 'security',
  },
  {
    id: 'security-audit',
    label: 'Security Audit',
    to: '/security-audit',
    icon: <BugReport />,
    permissions: [PERMISSIONS.VIEW_SECURITY, PERMISSIONS.MANAGE_SECURITY],
    category: 'security',
  },
  {
    id: 'compliance',
    label: 'Compliance',
    to: '/compliance',
    icon: <Policy />,
    permissions: [PERMISSIONS.VIEW_COMPLIANCE],
    category: 'security',
  },

  // User & Organization Management
  {
    id: 'users',
    label: 'Users',
    to: '/users',
    icon: <Group />,
    permissions: [PERMISSIONS.VIEW_USERS],
    category: 'organization',
  },
  {
    id: 'roles',
    label: 'Roles & Permissions',
    to: '/roles',
    icon: <SupervisorAccount />,
    permissions: [PERMISSIONS.MANAGE_ROLES],
    category: 'organization',
  },
  {
    id: 'org-settings',
    label: 'Organization',
    to: '/tenant/settings',
    icon: <Business />,
    permissions: [PERMISSIONS.VIEW_ORG_SETTINGS],
    category: 'organization',
  },

  // System Administration
  {
    id: 'system-admin',
    label: 'System Admin',
    to: '/system-admin',
    icon: <AdminPanelSettings />,
    permissions: [PERMISSIONS.MANAGE_SYSTEM],
    category: 'admin',
  },
  {
    id: 'backups',
    label: 'Backups',
    to: '/backups',
    icon: <Cloud />,
    permissions: [PERMISSIONS.MANAGE_BACKUPS],
    category: 'admin',
  },
  {
    id: 'system-config',
    label: 'Configuration',
    to: '/system-config',
    icon: <Build />,
    permissions: [PERMISSIONS.MANAGE_SYSTEM],
    category: 'admin',
  },

  // Notifications
  {
    id: 'notifications',
    label: 'Notifications',
    to: '/notifications',
    icon: <NotificationsIcon />,
    permissions: [PERMISSIONS.VIEW_ACTIVITY],
    category: 'misc',
  },

  // External & Support
  {
    id: 'role-demo',
    label: 'Role Demo',
    to: '/role-demo',
    icon: <SupervisorAccount />,
    permissions: [PERMISSIONS.VIEW_DASHBOARD],
    category: 'misc',
  },
  {
    id: 'marketplace',
    label: 'Marketplace',
    to: '/marketplace',
    icon: <Storefront />,
    permissions: [PERMISSIONS.VIEW_INTEGRATIONS],
    category: 'misc',
  },
  {
    id: 'docs',
    label: 'Documentation',
    to: '/docs',
    icon: <MenuBook />,
    permissions: [PERMISSIONS.VIEW_DOCS],
    category: 'misc',
  },
  {
    id: 'support',
    label: 'Support',
    to: '/support',
    icon: <HelpOutline />,
    permissions: [PERMISSIONS.VIEW_SUPPORT],
    category: 'misc',
  },
];

// Category definitions for menu grouping
export const MENU_CATEGORIES = {
  core: { label: 'Overview', order: 1 },
  agents: { label: 'Agent Management', order: 2 },
  tasks: { label: 'Task Management', order: 3 },
  analytics: { label: 'Analytics & Reports', order: 4 },
  billing: { label: 'Billing & Costs', order: 5 },
  monitoring: { label: 'Monitoring & Logs', order: 6 },
  integrations: { label: 'Integrations & APIs', order: 7 },
  development: { label: 'Development', order: 8 },
  security: { label: 'Security & Compliance', order: 9 },
  organization: { label: 'Organization', order: 10 },
  admin: { label: 'System Administration', order: 11 },
  misc: { label: 'Resources', order: 12 },
};

// Utility functions
export const hasPermission = (userRole, permission) => {
  const rolePermissions = ROLE_PERMISSIONS[userRole] || [];
  return rolePermissions.includes(permission);
};

export const hasAnyPermission = (userRole, permissions) => {
  return permissions.some(permission => hasPermission(userRole, permission));
};

export const getAccessibleMenuItems = userRole => {
  return NAVIGATION_ITEMS.filter(item =>
    hasAnyPermission(userRole, item.permissions)
  );
};

export const getMenuItemsByCategory = userRole => {
  const accessibleItems = getAccessibleMenuItems(userRole);
  const categorized = {};

  accessibleItems.forEach(item => {
    if (!categorized[item.category]) {
      categorized[item.category] = [];
    }
    categorized[item.category].push(item);
  });

  return categorized;
};

export const getRoleDisplayName = role => {
  const roleNames = {
    [USER_ROLES.OWNER]: 'Owner',
    [USER_ROLES.ADMIN]: 'Administrator',
    [USER_ROLES.MANAGER]: 'Manager',
    [USER_ROLES.DEVELOPER]: 'Developer',
    [USER_ROLES.ANALYST]: 'Analyst',
    [USER_ROLES.OPERATOR]: 'Operator',
    [USER_ROLES.VIEWER]: 'Viewer',
    [USER_ROLES.GUEST]: 'Guest',
    [USER_ROLES.INDIVIDUAL]: 'Individual',
    [USER_ROLES.DEMO]: 'Demo User',
  };
  return roleNames[role] || role;
};

export const getRoleColor = role => {
  const roleColors = {
    [USER_ROLES.OWNER]: 'error',
    [USER_ROLES.ADMIN]: 'warning',
    [USER_ROLES.MANAGER]: 'info',
    [USER_ROLES.DEVELOPER]: 'success',
    [USER_ROLES.ANALYST]: 'primary',
    [USER_ROLES.OPERATOR]: 'secondary',
    [USER_ROLES.VIEWER]: 'default',
    [USER_ROLES.GUEST]: 'default',
    [USER_ROLES.INDIVIDUAL]: 'secondary',
    [USER_ROLES.DEMO]: 'info',
  };
  return roleColors[role] || 'default';
};
