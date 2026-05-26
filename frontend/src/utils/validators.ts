import { z } from "zod";

export const emailSchema = z.string().email("Enter a valid email address");

export const passwordSchema = z
  .string()
  .min(10, "Password must be at least 10 characters")
  .regex(/[A-Z]/, "Must contain at least one uppercase letter")
  .regex(/[0-9]/, "Must contain at least one number");

export const uuidSchema = z.string().uuid("Invalid ID format");

export const positiveNumberSchema = z
  .number()
  .positive("Must be a positive number");

export const yearSchema = z
  .number()
  .int()
  .min(1990, "Year must be 1990 or later")
  .max(2100, "Year must be 2100 or earlier");

/**
 * Validate that a value is a valid ISO date string.
 */
export function isValidISODate(value: string): boolean {
  const date = new Date(value);
  return !isNaN(date.getTime());
}
