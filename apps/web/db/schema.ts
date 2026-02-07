import { pgTable, uuid, text, jsonb, timestamp } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

export const surveys = pgTable('surveys', {
  id: uuid('id').primaryKey().defaultRandom(),
  researchQuestion: text('research_question').notNull(),
  targetProfile: text('target_profile').notNull(),
  questions: jsonb('questions').notNull().$type<string[]>(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const responses = pgTable('responses', {
  id: uuid('id').primaryKey().defaultRandom(),
  surveyId: uuid('survey_id')
    .references(() => surveys.id, { onDelete: 'cascade' })
    .notNull(),
  data: jsonb('data').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Relations
export const surveysRelations = relations(surveys, ({ many }) => ({
  responses: many(responses),
}));

export const responsesRelations = relations(responses, ({ one }) => ({
  survey: one(surveys, {
    fields: [responses.surveyId],
    references: [surveys.id],
  }),
}));

// Types
export type Survey = typeof surveys.$inferSelect;
export type NewSurvey = typeof surveys.$inferInsert;
export type Response = typeof responses.$inferSelect;
export type NewResponse = typeof responses.$inferInsert;
