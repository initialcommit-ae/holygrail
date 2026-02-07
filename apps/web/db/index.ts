import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './schema';

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL environment variable is not set');
}

// Create the Neon serverless connection
const sql = neon(process.env.DATABASE_URL);

// Create the Drizzle instance
export const db = drizzle(sql, { schema });

// Export schema for convenience
export * from './schema';
