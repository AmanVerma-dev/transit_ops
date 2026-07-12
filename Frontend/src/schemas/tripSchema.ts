import { z } from 'zod';

// Static-shape validation for the "Create Trip" form. Cross-record checks
// (vehicle capacity vs cargo weight, driver licence expiry, vehicle/driver
// availability) remain in the page and run after this passes.
export const tripSchema = z.object({
  source: z.string().trim().min(1, 'Source is required.'),
  destination: z.string().trim().min(1, 'Destination is required.'),
  vehicleId: z.string().min(1, 'Vehicle is required.'),
  driverId: z.string().min(1, 'Driver is required.'),
  cargoWeight: z
    .string()
    .min(1, 'Cargo Weight (kg) is required.')
    .refine((v) => Number(v) > 0, 'Cargo Weight must be greater than 0.'),
  plannedDistance: z
    .string()
    .min(1, 'Planned Distance (km) is required.')
    .refine((v) => Number(v) > 0, 'Planned Distance must be greater than 0.'),
});

export type TripFormValues = z.infer<typeof tripSchema>;
