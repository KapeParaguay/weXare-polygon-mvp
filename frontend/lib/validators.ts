import { z } from "zod";

export const projectSchema = z.object({
  title: z.string().min(3),
  description: z.string().min(10)
});

export const disputeSchema = z.object({
  reason: z.string().min(5),
  evidence: z.string().url()
});

export const submitSchema = z.object({
  evidence: z.string().url()
});
