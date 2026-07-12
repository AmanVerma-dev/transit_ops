import { z } from 'zod';

// Static-shape validation for the "Log Service Record" dialog.
export const serviceRecordSchema = z.object({
  vehicleId: z.string().min(1, 'Vehicle is required.'),
  serviceType: z.string().trim().min(1, 'Service Type is required.'),
  cost: z
    .string()
    .min(1, 'Cost is required.')
    .refine((v) => Number(v) >= 0, 'Cost cannot be negative.'),
  date: z.string().trim().min(1, 'Date is required.'),
});

export type ServiceRecordFormValues = z.infer<typeof serviceRecordSchema>;
