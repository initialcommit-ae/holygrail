# SaaSv Database Setup with Neon DB

## Overview

This project uses [Neon DB](https://neon.com) - a serverless Postgres database optimized for modern applications. We use Drizzle ORM for type-safe database queries and migrations.

## Initial Setup

### 1. Create a Neon Database

1. Go to [https://neon.com](https://neon.com) and sign up
2. Create a new project (name it "saasv" or similar)
3. Copy the connection string from the dashboard
4. Add it to your `.env.local` file:

```bash
DATABASE_URL="postgresql://user:password@ep-xxx-xxx.neon.tech:5432/saasv?sslmode=require"
```

### 2. Push the Schema to Neon

```bash
pnpm db:push
```

This command will:
- Read your schema from `db/schema.ts`
- Push it directly to your Neon database
- Create all tables, enums, and relationships

### 3. (Optional) Generate Migrations

If you prefer migration files:

```bash
pnpm db:generate
```

This creates SQL migration files in `db/migrations/`

## Available Scripts

- `pnpm db:push` - Push schema changes directly to database (fastest for development)
- `pnpm db:generate` - Generate migration files from schema changes
- `pnpm db:migrate` - Run pending migrations
- `pnpm db:studio` - Open Drizzle Studio (visual database browser on localhost:4983)

## Database Schema

The schema is defined in `db/schema.ts` and includes:

### Core Tables

1. **businesses** - Client companies using the platform
2. **studies** - Research projects created by businesses
3. **research_briefs** - AI-generated research plans
4. **respondents** - WhatsApp users in the respondent pool
5. **conversations** - Individual interviews between Field Agent and respondents
6. **messages** - WhatsApp message history
7. **extractions** - Structured data extracted from completed conversations
8. **intelligence_briefs** - Final deliverables produced by Analyst Agent
9. **query_log** - Follow-up questions asked by businesses

### Key Features

- **JSONB fields** for flexible, nested data (objectives, targeting criteria, findings)
- **Enums** for status tracking and type safety
- **Foreign key relationships** to maintain data integrity
- **Timestamps** for audit trails
- **Decimal precision** for financial data

## Using the Database

Import the db instance and schema:

```typescript
import { db, businesses, studies } from '@/db';
import { eq } from 'drizzle-orm';

// Query examples
const allBusinesses = await db.select().from(businesses);
const study = await db.select().from(studies).where(eq(studies.id, studyId));

// Insert example
const newBusiness = await db.insert(businesses).values({
  name: 'Acme Corp',
  email: 'contact@acme.com',
  planTier: 'standard',
});
```

## Neon Features We Use

- **Serverless** - No connection pooling needed, works great with Next.js
- **Branching** - Create database branches for testing (like Git branches)
- **Auto-scaling** - Scales to zero when not in use
- **Edge-compatible** - Works in Vercel Edge Runtime

## Production Considerations

1. **Use connection pooling** for high-traffic scenarios
2. **Enable Neon branching** to test schema changes safely
3. **Set up backups** (Neon provides automatic backups on paid plans)
4. **Monitor query performance** using Neon's dashboard

## Troubleshooting

### Connection Issues

If you see "connection refused" errors:
- Verify your DATABASE_URL in `.env.local`
- Check that your Neon project is active
- Ensure SSL mode is set to `require`

### Type Errors

If TypeScript complains about types:
```bash
pnpm check-types
```

### Schema Changes Not Reflecting

```bash
# Push latest schema
pnpm db:push

# Or regenerate types
pnpm db:generate
```
