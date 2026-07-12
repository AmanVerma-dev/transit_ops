import { z } from 'zod';

// Static-shape validation for the "Log Fuel" dialog.
export const fuelSchema = z.object({
  vehicleId: z.string().min(1, 'Vehicle is required.'),
  date: z.string().trim().min(1, 'Date is required.'),
  liters: z
    .string()
    .min(1, 'Liters is required.')
    .refine((v) => Number(v) > 0, 'Liters must be greater than 0.'),
  cost: z
    .string()
    .min(1, 'Cost is required.')
    .refine((v) => Number(v) >= 0, 'Cost cannot be negative.'),
});

export type FuelFormValues = z.infer<typeof fuelSchema>;
