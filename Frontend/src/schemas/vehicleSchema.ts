import { z } from 'zod';
import type { VehicleType } from '../types';

// Static-shape validation for the "Add Vehicle" dialog. Cross-record checks
// (registration-number uniqueness) stay in the store and run after this passes.
export const vehicleSchema = z.object({
  regNo: z.string().trim().min(1, 'Registration number is required.'),
  name: z.string().trim().min(1, 'Name/Model is required.'),
  type: z.enum(['Van', 'Truck', 'Mini', 'Bus']),
  capacity: z
    .string()
    .min(1, 'Capacity (kg) is required.')
    .refine((v) => Number(v) > 0, 'Capacity must be greater than 0.'),
  odometer: z
    .string()
    .min(1, 'Odometer is required.')
    .refine((v) => Number(v) >= 0, 'Odometer cannot be negative.'),
  acquisitionCost: z
    .string()
    .min(1, 'Acquisition Cost is required.')
    .refine((v) => Number(v) >= 0, 'Acquisition Cost cannot be negative.'),
});

export type VehicleFormValues = z.infer<typeof vehicleSchema>;

export const VEHICLE_TYPES: VehicleType[] = ['Van', 'Truck', 'Mini', 'Bus'];
