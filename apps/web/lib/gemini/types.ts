import { z } from "zod";

export const demographicsSchema = z.object({
  ageRange: z.string().optional(),
  location: z.string().optional(),
  occupation: z.array(z.string()).optional(),
});

export const extractionSchema = z.object({
  objective: z.string().optional(),
  demographics: demographicsSchema.optional(),
  ready: z.boolean().optional(),
});

export type DemographicsOutput = z.infer<typeof demographicsSchema>;
export type ExtractionOutput = z.infer<typeof extractionSchema>;
