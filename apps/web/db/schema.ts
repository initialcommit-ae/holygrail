import { pgTable, uuid, text, timestamp, jsonb, integer, decimal, boolean, pgEnum } from 'drizzle-orm/pg-core';

// Enums
export const studyStatusEnum = pgEnum('study_status', [
  'draft',
  'review',
  'approved',
  'field',
  'analysis',
  'done',
]);

export const studyTypeEnum = pgEnum('study_type', [
  'quick_pulse',
  'standard',
  'deep_dive',
]);

export const conversationStatusEnum = pgEnum('conversation_status', [
  'invited',
  'accepted',
  'active',
  'complete',
  'abandoned',
]);

export const messageSenderEnum = pgEnum('message_sender', ['agent', 'respondent']);

export const respondentTierEnum = pgEnum('respondent_tier', [
  'community_voice',
  'active_contributor',
  'community_expert',
]);

// Tables
export const businesses = pgTable('businesses', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name').notNull(),
  email: text('email').notNull().unique(),
  planTier: text('plan_tier').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const studies = pgTable('studies', {
  id: uuid('id').primaryKey().defaultRandom(),
  businessId: uuid('business_id')
    .references(() => businesses.id)
    .notNull(),
  objectiveText: text('objective_text').notNull(),
  context: text('context'),
  status: studyStatusEnum('status').default('draft').notNull(),
  studyType: studyTypeEnum('study_type').notNull(),
  budgetTier: text('budget_tier'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
});

export const researchBriefs = pgTable('research_briefs', {
  id: uuid('id').primaryKey().defaultRandom(),
  studyId: uuid('study_id')
    .references(() => studies.id)
    .notNull(),
  version: integer('version').default(1).notNull(),
  decisionContext: text('decision_context').notNull(),
  infoObjectives: jsonb('info_objectives').notNull(), // Array of objective objects
  targeting: jsonb('targeting').notNull(), // Criteria + quotas
  sensitiveAreas: jsonb('sensitive_areas'), // Array of strings
  completionCriteria: jsonb('completion_criteria').notNull(),
  priorityRanking: jsonb('priority_ranking').notNull(), // Array of objective IDs
  approvedAt: timestamp('approved_at'),
});

export const respondents = pgTable('respondents', {
  id: uuid('id').primaryKey().defaultRandom(),
  phoneHash: text('phone_hash').notNull().unique(), // Hashed phone number for privacy
  whatsappId: text('whatsapp_id').notNull(), // For Twilio routing
  declaredAttrs: jsonb('declared_attrs').notNull(), // From onboarding
  derivedAttrs: jsonb('derived_attrs').default({}).notNull(), // From conversations
  reliabilityScore: decimal('reliability_score', { precision: 3, scale: 2 })
    .default('0.5')
    .notNull(),
  consistencyScore: decimal('consistency_score', { precision: 3, scale: 2 }),
  totalConvos: integer('total_convos').default(0).notNull(),
  tier: respondentTierEnum('tier').default('community_voice').notNull(),
  earningsTotal: decimal('earnings_total', { precision: 10, scale: 2 }).default('0').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  lastActive: timestamp('last_active'),
});

export const conversations = pgTable('conversations', {
  id: uuid('id').primaryKey().defaultRandom(),
  studyId: uuid('study_id')
    .references(() => studies.id)
    .notNull(),
  respondentId: uuid('respondent_id')
    .references(() => respondents.id)
    .notNull(),
  status: conversationStatusEnum('status').default('invited').notNull(),
  startedAt: timestamp('started_at'),
  completedAt: timestamp('completed_at'),
  durationSeconds: integer('duration_seconds'),
  compensationAmt: decimal('compensation_amt', { precision: 10, scale: 2 }),
  compensationPaid: boolean('compensation_paid').default(false).notNull(),
});

export const messages = pgTable('messages', {
  id: uuid('id').primaryKey().defaultRandom(),
  conversationId: uuid('conversation_id')
    .references(() => conversations.id)
    .notNull(),
  sender: messageSenderEnum('sender').notNull(),
  content: text('content').notNull(),
  metadata: jsonb('metadata'), // Objective tracker, internal notes (agent messages only)
  timestamp: timestamp('timestamp').defaultNow().notNull(),
  twilioSid: text('twilio_sid'), // For delivery tracking
});

export const extractions = pgTable('extractions', {
  id: uuid('id').primaryKey().defaultRandom(),
  conversationId: uuid('conversation_id')
    .references(() => conversations.id)
    .notNull()
    .unique(), // One per completed conversation
  respondentProfile: jsonb('respondent_profile').notNull(), // Enriched from conversation
  objectiveCoverage: jsonb('objective_coverage').notNull(), // Per-objective status + summary
  unexpectedFindings: jsonb('unexpected_findings'),
  confidenceFlags: jsonb('confidence_flags').notNull(),
  derivedAttrsNew: jsonb('derived_attrs_new'), // New attributes discovered
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const intelligenceBriefs = pgTable('intelligence_briefs', {
  id: uuid('id').primaryKey().defaultRandom(),
  studyId: uuid('study_id')
    .references(() => studies.id)
    .notNull(),
  execSummary: text('exec_summary').notNull(),
  findings: jsonb('findings').notNull(), // Array of findings with confidence
  demographics: jsonb('demographics'),
  tensions: jsonb('tensions'),
  recommendations: jsonb('recommendations'),
  methodology: jsonb('methodology').notNull(), // Sample description, timeline
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const queryLog = pgTable('query_log', {
  id: uuid('id').primaryKey().defaultRandom(),
  studyId: uuid('study_id')
    .references(() => studies.id)
    .notNull(),
  businessId: uuid('business_id')
    .references(() => businesses.id)
    .notNull(),
  question: text('question').notNull(),
  answer: text('answer').notNull(),
  sourcesUsed: jsonb('sources_used'), // Which extractions cited
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Types (for TypeScript usage)
export type Business = typeof businesses.$inferSelect;
export type NewBusiness = typeof businesses.$inferInsert;

export type Study = typeof studies.$inferSelect;
export type NewStudy = typeof studies.$inferInsert;

export type ResearchBrief = typeof researchBriefs.$inferSelect;
export type NewResearchBrief = typeof researchBriefs.$inferInsert;

export type Respondent = typeof respondents.$inferSelect;
export type NewRespondent = typeof respondents.$inferInsert;

export type Conversation = typeof conversations.$inferSelect;
export type NewConversation = typeof conversations.$inferInsert;

export type Message = typeof messages.$inferSelect;
export type NewMessage = typeof messages.$inferInsert;

export type Extraction = typeof extractions.$inferSelect;
export type NewExtraction = typeof extractions.$inferInsert;

export type IntelligenceBrief = typeof intelligenceBriefs.$inferSelect;
export type NewIntelligenceBrief = typeof intelligenceBriefs.$inferInsert;

export type QueryLog = typeof queryLog.$inferSelect;
export type NewQueryLog = typeof queryLog.$inferInsert;
