import { z } from 'zod';
import type { LicenseCategory } from '../types';

// Static-shape validation for the "Add Driver" dialog. The MM/YYYY licence
// expiry format is enforced here; assignment availability checks remain in the
// store/page logic.
export const driverSchema = z.object({
  name: z.string().trim().min(1, 'Name is required.'),
  licenseNo: z.string().trim().min(1, 'License No. is required.'),
  category: z.enum(['LMV', 'HMV']),
  licenseExpiry: z
    .string()
    .min(1, 'License Expiry is required.')
    .regex(/^\d{2}\/\d{4}$/, 'License expiry must be in MM/YYYY format.'),
  contact: z.string().trim().min(1, 'Contact is required.'),
});

export type DriverFormValues = z.infer<typeof driverSchema>;

export const LICENSE_CATEGORIES: LicenseCategory[] = ['LMV', 'HMV'];
