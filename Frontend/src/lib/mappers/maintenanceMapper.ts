import type { MaintenanceLog, MaintenanceStatus, MaintenanceType } from '../../types';

export interface BackendMaintenance {
  id: number;
  vehicle_id: number;
  maintenance_type: string;
  description: string;
  scheduled_date: string;
  started_at: string | null;
  completed_at: string | null;
  estimated_cost: number;
  actual_cost: number | null;
  status: string;
  technician_notes: string | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

const STATUS_MAP: Record<string, MaintenanceStatus> = {
  SCHEDULED: 'Scheduled',
  IN_PROGRESS: 'In Progress',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

export function maintenanceToFrontend(b: BackendMaintenance, vehicleName: string): MaintenanceLog {
  const displayCost = b.actual_cost ?? b.estimated_cost;
  return {
    id: String(b.id),
    vehicleId: String(b.vehicle_id),
    vehicleName,
    maintenanceType: b.maintenance_type as MaintenanceType,
    serviceType: b.description,
    estimatedCost: b.estimated_cost,
    actualCost: b.actual_cost ?? undefined,
    cost: displayCost,
    scheduledDate: b.scheduled_date,
    date: formatDate(b.scheduled_date),
    technicianNotes: b.technician_notes ?? undefined,
    status: STATUS_MAP[b.status] || 'Scheduled',
  };
}

export function maintenanceCreateToBackend(f: {
  vehicleId: string;
  maintenanceType: MaintenanceType;
  description: string;
  estimatedCost: number;
  technicianNotes?: string;
}) {
  return {
    vehicle_id: parseInt(f.vehicleId, 10),
    maintenance_type: f.maintenanceType,
    description: f.description,
    scheduled_date: new Date().toISOString(),
    estimated_cost: f.estimatedCost,
    technician_notes: f.technicianNotes || null,
  };
}
