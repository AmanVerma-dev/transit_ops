import { z } from 'zod';
import type { MaintenanceType } from '../types';

export const MAINTENANCE_TYPES: MaintenanceType[] = ['Preventive', 'Corrective', 'Emergency', 'Inspection'];

// Static-shape validation for the "Log Service Record" dialog.
export const serviceRecordSchema = z.object({
  vehicleId: z.string().min(1, 'Vehicle is required.'),
  maintenanceType: z.enum(['Preventive', 'Corrective', 'Emergency', 'Inspection'], {
    errorMap: () => ({ message: 'Maintenance Type is required.' }),
  }),
  serviceType: z.string().trim().min(1, 'Service Type is required.'),
  estimatedCost: z
    .string()
    .min(1, 'Estimated Cost is required.')
    .refine((v) => Number(v) >= 0, 'Cost cannot be negative.'),
  technicianNotes: z.string().optional(),
});

export type ServiceRecordFormValues = z.infer<typeof serviceRecordSchema>;
