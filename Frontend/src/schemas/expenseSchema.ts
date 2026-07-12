import { z } from 'zod';

// Static-shape validation for the "Add Expense" dialog.
export const expenseSchema = z.object({
  tripId: z.string().trim().min(1, 'Trip ID is required.'),
  vehicleId: z.string().min(1, 'Vehicle is required.'),
  toll: z
    .string()
    .min(1, 'Toll is required.')
    .refine((v) => Number(v) >= 0, 'Toll cannot be negative.'),
  other: z
    .string()
    .min(1, 'Other is required.')
    .refine((v) => Number(v) >= 0, 'Other cannot be negative.'),
});

export type ExpenseFormValues = z.infer<typeof expenseSchema>;
