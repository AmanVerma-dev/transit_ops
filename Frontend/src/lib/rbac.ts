import type { Role, PermissionLevel, RbacEntry } from '../types';

export const RBAC_MATRIX: RbacEntry[] = [
  { role: 'Fleet Manager',     fleet: 'full', drivers: 'full', trips: 'none', fuelExp: 'none', analytics: 'view' },
  { role: 'Dispatcher',        fleet: 'view', drivers: 'none', trips: 'full', fuelExp: 'none', analytics: 'none' },
  { role: 'Safety Officer',    fleet: 'none', drivers: 'full', trips: 'view', fuelExp: 'none', analytics: 'none' },
  { role: 'Financial Analyst', fleet: 'none', drivers: 'none', trips: 'view', fuelExp: 'full', analytics: 'full' },
];

export type RouteModule = 'fleet' | 'drivers' | 'trips' | 'fuelExp' | 'analytics' | 'dashboard' | 'settings' | 'maintenance';

const ROUTE_TO_MODULE: Record<string, RouteModule> = {
  '/fleet':          'fleet',
  '/drivers':        'drivers',
  '/trips':          'trips',
  '/fuel-expenses':  'fuelExp',
  '/analytics':      'analytics',
  '/dashboard':      'dashboard',
  '/settings':       'settings',
  '/maintenance':    'maintenance',
};

export function getPermission(role: Role, module: RouteModule): PermissionLevel {
  // Dashboard and Settings are accessible to all roles
  if (module === 'dashboard' || module === 'settings') return 'full';
  // Maintenance follows Fleet Manager permission
  if (module === 'maintenance') {
    const entry = RBAC_MATRIX.find(e => e.role === role);
    return entry?.fleet ?? 'none';
  }
  const entry = RBAC_MATRIX.find(e => e.role === role);
  if (!entry) return 'none';
  return entry[module as keyof Omit<RbacEntry, 'role'>] ?? 'none';
}

export function canAccessRoute(role: Role, path: string): boolean {
  // Extract the base route, e.g. "/fleet/123" -> "/fleet"
  const baseRoute = '/' + path.split('/')[1];
  const module = ROUTE_TO_MODULE[baseRoute];
  if (!module) return true;
  return getPermission(role, module) !== 'none';
}

export function getAccessibleNavItems(role: Role) {
  const allItems = [
    { label: 'Dashboard',        path: '/dashboard',      icon: 'LayoutDashboard' },
    { label: 'Fleet',            path: '/fleet',           icon: 'Truck' },
    { label: 'Drivers',          path: '/drivers',         icon: 'Users' },
    { label: 'Trips',            path: '/trips',           icon: 'Route' },
    { label: 'Maintenance',      path: '/maintenance',     icon: 'Wrench' },
    { label: 'Fuel & Expenses',  path: '/fuel-expenses',   icon: 'Fuel' },
    { label: 'Analytics',        path: '/analytics',       icon: 'BarChart3' },
    { label: 'Settings',         path: '/settings',        icon: 'Settings' },
  ];
  return allItems.filter(item => canAccessRoute(role, item.path));
}

export function getDefaultRoute(_role: Role): string {
  return '/dashboard';
}
