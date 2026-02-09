import {
  pgTable,
  uuid,
  text,
  jsonb,
  timestamp,
  integer,
  uniqueIndex,
  index,
} from 'drizzle-orm/pg-core';
import { relations, sql } from 'drizzle-orm';

// --- Users ---

export const users = pgTable(
  'users',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    phoneNumber: text('phone_number').notNull(),
    status: text('status').notNull().default('new'),
    city: text('city'),
    neighborhood: text('neighborhood'),
    ageRange: text('age_range'),
    gender: text('gender'),
    createdAt: timestamp('created_at', { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => [uniqueIndex('uq_users_phone').on(table.phoneNumber)],
);

// --- Campaigns ---

export const campaigns = pgTable('campaigns', {
  id: uuid('id').primaryKey().defaultRandom(),
  name: text('name').notNull(),
  researchBrief: text('research_brief').notNull(),
  extractionSchema: jsonb('extraction_schema').notNull().$type<
    Record<string, { type: string; description: string }>
  >(),
  systemPromptOverride: text('system_prompt_override'),
  rewardText: text('reward_text'),
  rewardLink: text('reward_link'),
  phoneNumbers: text('phone_numbers').array(),
  targeting: jsonb('targeting').$type<Record<string, unknown> | null>(),
  status: text('status').notNull().default('draft'),
  totalConversations: integer('total_conversations').notNull().default(0),
  completedConversations: integer('completed_conversations')
    .notNull()
    .default(0),
  createdAt: timestamp('created_at', { withTimezone: true })
    .defaultNow()
    .notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true })
    .defaultNow()
    .notNull(),
});

// --- Conversations ---

export const conversations = pgTable(
  'conversations',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    campaignId: uuid('campaign_id')
      .references(() => campaigns.id, { onDelete: 'cascade' }),
    userId: uuid('user_id')
      .references(() => users.id, { onDelete: 'cascade' })
      .notNull(),
    phoneNumber: text('phone_number').notNull(),
    status: text('status').notNull().default('pending'),
    extractedData: jsonb('extracted_data')
      .default({})
      .$type<Record<string, unknown>>(),
    messageCount: integer('message_count').notNull().default(0),
    createdAt: timestamp('created_at', { withTimezone: true })
      .defaultNow()
      .notNull(),
    updatedAt: timestamp('updated_at', { withTimezone: true })
      .defaultNow()
      .notNull(),
    completedAt: timestamp('completed_at', { withTimezone: true }),
  },
  (table) => [
    uniqueIndex('uq_campaign_phone')
      .on(table.campaignId, table.phoneNumber)
      .where(sql`campaign_id IS NOT NULL`),
    index('idx_conversations_phone').on(table.phoneNumber),
    index('idx_conversations_status').on(table.campaignId, table.status),
  ],
);

// --- Messages ---

export const messages = pgTable(
  'messages',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    conversationId: uuid('conversation_id')
      .references(() => conversations.id, { onDelete: 'cascade' })
      .notNull(),
    sender: text('sender').notNull(), // 'agent' | 'user'
    content: text('content').notNull(),
    twilioSid: text('twilio_sid'),
    createdAt: timestamp('created_at', { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => [
    index('idx_messages_conversation').on(
      table.conversationId,
      table.createdAt,
    ),
    uniqueIndex('uq_messages_twilio_sid')
      .on(table.twilioSid)
      .where(sql`twilio_sid IS NOT NULL`),
  ],
);

// --- Outreach Queue ---

export const outreachQueue = pgTable(
  'outreach_queue',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    conversationId: uuid('conversation_id')
      .references(() => conversations.id, { onDelete: 'cascade' })
      .notNull(),
    scheduledAt: timestamp('scheduled_at', { withTimezone: true }).notNull(),
    sentAt: timestamp('sent_at', { withTimezone: true }),
    status: text('status').notNull().default('pending'),
    error: text('error'),
    createdAt: timestamp('created_at', { withTimezone: true })
      .defaultNow()
      .notNull(),
  },
  (table) => [
    index('idx_outreach_pending').on(table.status, table.scheduledAt),
  ],
);

// --- Relations ---

export const usersRelations = relations(users, ({ many }) => ({
  conversations: many(conversations),
}));

export const campaignsRelations = relations(campaigns, ({ many }) => ({
  conversations: many(conversations),
}));

export const conversationsRelations = relations(
  conversations,
  ({ one, many }) => ({
    campaign: one(campaigns, {
      fields: [conversations.campaignId],
      references: [campaigns.id],
    }),
    user: one(users, {
      fields: [conversations.userId],
      references: [users.id],
    }),
    messages: many(messages),
    outreachQueue: many(outreachQueue),
  }),
);

export const messagesRelations = relations(messages, ({ one }) => ({
  conversation: one(conversations, {
    fields: [messages.conversationId],
    references: [conversations.id],
  }),
}));

export const outreachQueueRelations = relations(outreachQueue, ({ one }) => ({
  conversation: one(conversations, {
    fields: [outreachQueue.conversationId],
    references: [conversations.id],
  }),
}));

// --- Types ---

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type Campaign = typeof campaigns.$inferSelect;
export type NewCampaign = typeof campaigns.$inferInsert;
export type Conversation = typeof conversations.$inferSelect;
export type NewConversation = typeof conversations.$inferInsert;
export type Message = typeof messages.$inferSelect;
export type NewMessage = typeof messages.$inferInsert;
export type OutreachQueueItem = typeof outreachQueue.$inferSelect;
export type NewOutreachQueueItem = typeof outreachQueue.$inferInsert;
