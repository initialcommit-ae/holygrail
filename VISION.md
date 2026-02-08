# MeshAI — Paid Side Quests on Your Phone

MeshAI is a paid research network that lives entirely inside WhatsApp. Companies need real opinions. People have opinions and want money. We connect them through short, fun, conversational research chats — and pay instantly.

No apps to download. No forms to fill. No accounts to create. Just WhatsApp.

---

## The Experience

### What it feels like

Your phone buzzes. It's a new bounty:

> 🎯 New bounty: A company wants to know about your coffee habits. ~4 min · AED 15 Amazon gift card
> Reply 'go' to start!

You reply "go." A quick, natural conversation happens — not a survey, not a form, just a chat. Four minutes later:

> That's everything — thanks! Here's your AED 15 Amazon gift card: https://reward.link/abc123
> Enjoy your next coffee ☕

Your phone buzzes again the next day. Another bounty. You do it while waiting for your food. AED 20 in 5 minutes.

That's MeshAI. Paid side quests on your phone.

### Design principles

**Value first, always.** Every interaction leads with what the user gets. The bounty amount and reward are the first thing they see. We never ask for anything before showing what's in it for them.

**Zero friction.** No sign-up flow. No app. No password. WhatsApp is the entire interface. The first message a user ever sees either comes from an ad click (one tap) or a bounty that arrived in their inbox. Onboarding happens invisibly, woven into the first conversation.

**Fun, not corporate.** The tone is casual, warm, quick. This is WhatsApp, not an enterprise survey tool. Messages are 1-3 sentences. The agent has personality. Emojis are natural, not forced. It feels like texting a friend who happens to pay you.

**Instant gratification.** The reward link arrives the moment the conversation ends. No "please allow 3-5 business days." No points system. No minimum balance. You finish, you get paid. Right there in the same chat.

**Respect attention.** We send bounties, not spam. If a user ignores a bounty, we don't follow up. If they say no, we say "no worries" and move on. Every message earns the right to send the next one.

**Side quests are sacred.** When a user is in an active campaign conversation, that time belongs to the conversation. New bounties are still queued for them — they can always be targeted — but the notification doesn't go out until the current side quest is done. No interruptions, no split attention. They finish, they get paid, and then the next bounty arrives.

---

## The Three Modes

Every message in a user's WhatsApp thread falls into one of three modes. The system detects which mode applies and uses the appropriate agent behavior.

### Mode 1: Onboarding

**When:** A new person messages the MeshAI number for the first time (organic or via ad click).

**Purpose:** Welcome them to the network, explain what MeshAI is, collect basic demographics so we can match them with relevant bounties.

**What happens:**

```
User: "JOIN"  (preset message from ad link)

Agent: "Welcome to MeshAI! We send you paid research
        chats on WhatsApp — companies need real opinions
        and you get rewarded for yours. 💰

        Quick setup so we match you with the right ones —
        what city are you in?"

User: "Abu Dhabi"

Agent: "Nice — which part of Abu Dhabi? Like what
        neighborhood or area?"

User: "Yas Island"

Agent: "And what's your age range?
        18-24 / 25-34 / 35-44 / 45+?"

User: "25-34"

Agent: "Last one — how do you identify?
        Male / Female / Other"

User: "Male"

Agent: "You're all set! We'll send bounties your way
        as they come up. 🎯"
```

**Demographics collected:**
- City (required — agent insists)
- Neighborhood (optional — agent probes once, accepts if user doesn't specify)
- Age range (required — predefined brackets)
- Gender (required)

**After onboarding:** User is marked as `onboarded` and enters the pool. They wait for bounties.

### Mode 2: Bounty Delivery

**When:** A campaign targets this user and they're not mid-conversation.

**Purpose:** Present a paid opportunity. Let the user decide if they want to do it.

**What happens:**

```
Agent: "🎯 New bounty: A company is researching gym
        and fitness habits in Abu Dhabi.
        ~5 min · AED 25 Amazon gift card
        Reply 'go' to start!"
```

The user can:
- **Accept** ("go", "sure", "yes", "let's do it") → transitions to Campaign mode
- **Decline** ("no", "pass", "not now") → agent says "No worries, catch you next time!" and the bounty is marked declined
- **Ignore** → no follow-up, bounty expires after a configurable window

**Bounty rules:**
- Bounties arrive throughout the day, proactively pushed to the user
- Users can always be targeted for new bounties by any campaign — targeting never stops
- But if the user is in an active side quest, the bounty notification is held and delivered after the conversation ends — side quest time is sacred
- Only one bounty notification at a time — no stacking multiple offers in rapid succession
- No reminders, no "hey you haven't responded to that bounty"

### Mode 3: Campaign Conversation

**When:** User accepted a bounty. This is the core product.

**Purpose:** Conduct a goal-driven research conversation. Extract specific data points through natural dialogue.

**What happens:**

```
Agent: "Let's do it! 🚀
        So what gym do you go to these days?"

User: "Fitness First in Yas Mall"

Agent: "Solid choice. How often do you go in
        a typical week?"

User: "Like 3-4 times"

Agent: "Nice consistency. What made you pick
        Fitness First over other options?"

User: "Closest to my place and the price
        is decent"

  ... a few more exchanges ...

Agent: "That's everything — thanks! 🎉
        Here's your AED 25 Amazon gift card:
        https://reward.link/xyz789
        Enjoy!"
```

**How the agent works:**
- The agent receives the campaign's research brief and extraction schema (specific data points to collect)
- It sees the full conversation history and what data has been collected so far
- It decides what to ask next — there is no script, no fixed question order
- It acknowledges what the person said before changing topics
- It probes vague answers before moving on
- It keeps messages short (1-3 sentences)
- When all data points are collected, it ends the conversation and delivers the reward link
- If the user is new (outbound path, not yet onboarded), the agent weaves demographic questions in naturally at the start before diving into research

**What makes this different from a survey:**

| Survey Bot | MeshAI Agent |
|---|---|
| "Question 1 of 7: What is your age?" | "So what gym do you go to these days?" |
| Fixed question order | Agent decides based on conversation flow |
| Ignores context from previous answers | "Fitness First — solid choice. How often do you go?" |
| Same script for everyone | Each conversation is unique |
| Hard cutoff at question N | Agent decides when it has enough |
| "Survey complete." | "Here's your gift card: [link]" |

---

## User Lifecycle

```
                         ┌─────────────────┐
                         │    UNKNOWN       │
                         │  (not in system) │
                         └────────┬────────┘
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                 │
            They message     Click ad/link     Business provides
            us first         preset message    their phone number
            (organic)        (inbound)         (outbound)
                 │                │                 │
                 ▼                ▼                 │
           ┌──────────────────────────┐            │
           │  ONBOARDING              │            │
           │  status: "onboarding"    │            │
           │                          │            │
           │  Collect demographics    │            │
           │  → city                  │            │
           │  → neighborhood          │            │
           │  → age_range             │            │
           │  → gender                │            │
           └────────────┬─────────────┘            │
                        │                          │
                        ▼                          │
           ┌──────────────────────────┐            │
           │  ONBOARDED               │            │
           │  status: "onboarded"     │            │
           │                          │            │
           │  In the pool.            │◄───────────┘
           │  Receives bounties.      │     Bounty arrives.
           │                          │     If they accept,
           └────────────┬─────────────┘     demographics are
                        │                   collected during
                   Bounty arrives           the campaign convo.
                        │                   → becomes "onboarded"
                        ▼                      after first campaign.
           ┌──────────────────────────┐
           │  BOUNTY RECEIVED         │
           │                          │
           │  Accept → Campaign       │
           │  Decline → back to pool  │
           │  Ignore → expires        │
           └──────────────────────────┘
                        │
                     Accept
                        │
                        ▼
           ┌──────────────────────────┐
           │  IN CAMPAIGN             │
           │                          │
           │  Goal-driven research    │
           │  conversation.           │
           │  No new bounties until   │
           │  this one completes.     │
           └────────────┬─────────────┘
                        │
                   Conversation
                   complete
                        │
                        ▼
           ┌──────────────────────────┐
           │  REWARD DELIVERED        │
           │                          │
           │  Link sent in chat.      │
           │  Back to pool.           │
           │  Ready for next bounty.  │
           └──────────────────────────┘
```

---

## Data Model

### users

The identity layer. One row per phone number. No PII beyond phone — demographics are category-level.

```
users
├── id                  uuid PK
├── phone_number        text UNIQUE
├── status              "new" | "onboarding" | "onboarded"
├── city                text           "Abu Dhabi"
├── neighborhood        text?          "Yas Island" (nullable)
├── age_range           text           "25-34"
├── gender              text           "Male"
└── created_at          timestamptz
```

### campaigns

What a business creates. Defines the research goal, what data to extract, and what to pay.

```
campaigns
├── id                      uuid PK
├── name                    text           "Gas station feasibility"
├── research_brief          text           "Understand refueling habits..."
├── extraction_schema       jsonb          { "satisfaction": { type, description }, ... }
├── reward_text             text           "AED 20 Amazon gift card"
├── reward_link             text           "https://reward.link/template/..."
├── system_prompt_override  text?          Optional custom agent instructions
├── phone_numbers           text[]?        Business-provided list (outbound)
├── targeting               jsonb?         { city: "Abu Dhabi", gender: "Male", ... }
├── status                  "draft" | "active" | "paused" | "completed"
├── total_conversations     int
├── completed_conversations int
└── created_at / updated_at timestamptz
```

Two ways to populate:
- `phone_numbers` — business provides a list (outbound, may include people not in the network)
- `targeting` — match from the onboarded user pool by demographics

### conversations

One per user per campaign (or one for onboarding with no campaign).

```
conversations
├── id                  uuid PK
├── user_id             uuid FK → users
├── campaign_id         uuid FK → campaigns (NULL for onboarding)
├── phone_number        text              Denormalized for webhook lookup
├── status              (see state machine below)
├── extracted_data      jsonb             { "satisfaction": 7, ... }
├── message_count       int
└── created_at / updated_at / completed_at  timestamptz
```

### messages

Every message ever sent or received.

```
messages
├── id                  uuid PK
├── conversation_id     uuid FK → conversations
├── sender              "agent" | "user"
├── content             text
├── twilio_sid          text?
└── created_at          timestamptz
```

### outreach_queue

Staggered scheduling for bounty delivery and outbound messages.

```
outreach_queue
├── id                  uuid PK
├── conversation_id     uuid FK → conversations
├── scheduled_at        timestamptz
├── sent_at             timestamptz?
├── status              "pending" | "sent" | "failed"
├── error               text?
└── created_at          timestamptz
```

---

## State Machines

### Campaign Status

```
draft ──(launch)──→ active ──(all conversations done)──→ completed
                       │
                       │ (researcher pauses)
                       ▼
                    paused ──(resume/re-launch)──→ active
```

### Conversation Status

**Onboarding conversation** (campaign_id = NULL):

```
active ──(demographics collected)──→ completed
   │
   └──(user stops / "stop")──→ abandoned
```

**Campaign conversation** (campaign_id set):

```
pending ──(bounty sent)──→ bounty_sent ──(user accepts)──→ active ──(all data collected)──→ completed
                               │                              │
                               │ (user declines)              │ (user says "stop")
                               ▼                              ▼
                           declined                       abandoned

                               │ (no response)
                               ▼
                           expired
```

### User Status

```
new ──(starts onboarding or first campaign)──→ onboarding ──(demographics filled)──→ onboarded
```

---

## Message Routing

Every inbound WhatsApp message hits a single webhook. The system figures out what to do.

```
POST /twilio/inbound
     │
     ▼
Normalize phone number
Return 200 immediately
Background task:
     │
     ▼
┌─ Lookup user by phone ─────────────────────────────────────────┐
│                                                                 │
│  NOT FOUND                          FOUND                       │
│  │                                  │                           │
│  ▼                                  ▼                           │
│  Create user (status="new")    Find active conversation:        │
│  Create onboarding convo       SELECT WHERE user_id = $id       │
│  → ONBOARDING PROMPT           AND status IN ('active',         │
│                                    'bounty_sent')               │
│                                     │                           │
│                           ┌─────────┴──────────┐                │
│                           │                    │                │
│                        FOUND              NOT FOUND             │
│                           │                    │                │
│                           ▼                    ▼                │
│                    What's the status?     User is idle.          │
│                           │                No active convo.     │
│              ┌────────────┼────────┐       Could be random       │
│              │            │        │       message or question.  │
│              ▼            ▼        ▼       → GENERAL PROMPT      │
│         bounty_sent    active   active                          │
│         (campaign)   (campaign) (onboarding)                    │
│              │            │        │                             │
│              ▼            ▼        ▼                             │
│         Interpret     CAMPAIGN   ONBOARDING                     │
│         accept/       PROMPT     PROMPT                         │
│         decline                                                 │
│              │                                                   │
│         ┌────┴────┐                                              │
│         │         │                                              │
│      Accept    Decline                                           │
│         │         │                                              │
│         ▼         ▼                                              │
│    → CAMPAIGN  Mark declined                                     │
│      PROMPT    "No worries!"                                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## The Three Agent Prompts

### Onboarding Prompt

Used for: organic joins, ad click joins — no campaign attached.

```
You are MeshAI's welcome agent. MeshAI pays people for short
research chats on WhatsApp.

A new person just messaged. Your job:
1. Welcome them warmly. Explain MeshAI in one sentence.
2. Collect their demographics naturally:
   - city (required — ask directly)
   - neighborhood (probe once — "which part of [city]?")
   - age_range (required — offer brackets: 18-24, 25-34, 35-44, 45+)
   - gender (required — Male / Female / Other)
3. When done, tell them they're set and bounties will come their way.

Keep it casual. This is WhatsApp. 1-3 sentences per message.
Be fun, not corporate.
```

### General Prompt

Used for: onboarded users who message while idle (no active conversation).

```
You are MeshAI's assistant. This person is in the MeshAI
paid research network.

They've messaged outside of an active bounty. They might be:
- Asking how MeshAI works
- Asking about rewards or payments
- Just saying hi
- Asking when the next bounty is

Be friendly, brief, helpful. If they ask when the next bounty is,
tell them we'll send one when something matches their profile.
If they have a question you can't answer, tell them to reach out
to support.

Keep it to 1-2 sentences. Don't over-explain.
```

### Campaign Prompt

Used for: active research conversations after a bounty is accepted. This is the goal-driven agent.

```
You are a friendly research agent conducting a paid conversation
over WhatsApp for MeshAI.

REWARD: {reward_text}
RESEARCH CONTEXT: {research_brief}

KNOWN ABOUT THIS PERSON:
- city: {city or "unknown"}
- neighborhood: {neighborhood or "unknown"}
- age_range: {age_range or "unknown"}
- gender: {gender or "unknown"}

DATA POINTS TO COLLECT:
{extraction_schema formatted}

ALREADY COLLECTED:
{extracted_data formatted}

STILL NEEDED:
{remaining fields formatted}

{system_prompt_override if set}

RULES:
1. Your first message after they accept should signal the start
   clearly — make it feel like "we're doing this!"
2. If any demographics above are "unknown", weave them in naturally
   at the start before the research questions.
3. Ask ONE question at a time. 1-3 sentences max.
4. Acknowledge what the person said before changing topics.
5. Use natural transitions. Never reveal you have a checklist.
6. Probe vague answers before moving on.
7. Be warm, fun, curious. This should feel enjoyable.
8. When ALL data points are collected with concrete answers,
   send a thank-you message and include the reward link.
   Set conversation_complete = true.
```

---

## Structured Agent Output

Every agent call returns:

```
AgentResponse
├── message                    str       Next WhatsApp message to send
├── extracted_data_update      dict      Campaign data points from this exchange
├── user_demographics_update   dict      Demographics from this exchange (city, age, etc.)
├── conversation_complete      bool      All done?
├── bounty_accepted            bool?     For bounty_sent status — did they accept?
└── internal_reasoning         str       Agent's strategy notes (not sent to user)
```

`user_demographics_update` flows into the `users` table — whether it's during onboarding or woven into a campaign conversation. Once all four demographics are filled, user status becomes `onboarded`.

---

## Campaign Launch Flow — Step by Step

### Step 1: Business creates a campaign

```
POST /campaigns
{
  "name": "Gas station feasibility - Abu Dhabi",
  "research_brief": "We want to understand refueling habits of commuters
                     in Abu Dhabi. We're evaluating opening a new station.",
  "extraction_schema": {
    "current_station": { "type": "string", "description": "Where they refuel" },
    "visit_frequency": { "type": "string", "description": "How often per week" },
    "satisfaction":    { "type": "number", "description": "1-10 rating" },
    "switch_reason":   { "type": "string", "description": "What would make them switch" },
    "monthly_spend":   { "type": "string", "description": "Approx monthly fuel spend" }
  },
  "reward_text": "AED 20 Amazon gift card",
  "reward_link": "https://reward.mesh.ai/gc/amzn20",
  "phone_numbers": ["+971501234567", "+971509876543", ...]
}
```

Campaign created with status `draft`.

### Step 2: Launch

```
POST /campaigns/{id}/launch
```

For each phone number:

```
┌─ Is this phone number in the network? ────────────────────────┐
│                                                                │
│  YES (user exists, status = "onboarded")                       │
│  → Create conversation (status = "pending")                    │
│  → Schedule bounty in outreach_queue                           │
│                                                                │
│  YES (user exists, status = "onboarding" or "new")             │
│  → Create conversation (status = "pending")                    │
│  → Schedule bounty in outreach_queue                           │
│  → Agent will collect demographics during the campaign         │
│                                                                │
│  NO (unknown number)                                           │
│  → Create user (status = "new")                                │
│  → Create conversation (status = "pending")                    │
│  → Schedule bounty in outreach_queue                           │
│  → First message includes brief MeshAI intro + bounty          │
│  → Agent will collect demographics during the campaign         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Step 3: Outreach worker sends bounties

The background worker picks up scheduled items and sends bounty messages:

**To a known, onboarded user:**
```
🎯 New bounty: A company is researching gas station
habits in Abu Dhabi.
~5 min · AED 20 Amazon gift card
Reply 'go' to start!
```

**To a new/unknown user:**
```
Hey! This is MeshAI — we pay people for quick
research chats on WhatsApp. 💰

🎯 Your first bounty: Gas station habits in Abu Dhabi.
~5 min · AED 20 Amazon gift card
Reply 'go' to start!
```

Conversation status → `bounty_sent`.

### Step 4: User accepts

User replies "go" (or "sure", "yes", "let's do it", etc.)

The agent interprets this as acceptance:
- Conversation status → `active`
- Agent switches to the Campaign Prompt
- If user demographics are missing, agent weaves them in early
- Research conversation begins

### Step 5: Conversation plays out

```
Agent: "Let's do it! 🚀 Where do you usually fill up?"
User:  "ADNOC on the highway near Yas"
       → extracted: { current_station: "ADNOC, highway near Yas Island" }

Agent: "Classic spot. How often do you stop there — like weekly?"
User:  "Probably twice a week"
       → extracted: { visit_frequency: "twice a week" }

Agent: "And how would you rate ADNOC overall, 1 to 10?"
User:  "Hmm like a 7, it's fine but nothing special"
       → extracted: { satisfaction: 7 }

Agent: "Fair enough. What would actually make you switch to a different station?"
User:  "If there was one closer to my house with a car wash"
       → extracted: { switch_reason: "closer location with car wash" }

Agent: "Makes sense. Last thing — roughly how much do you spend on fuel a month?"
User:  "Around 500-600 dirhams"
       → extracted: { monthly_spend: "500-600 AED" }
       → all fields filled → conversation_complete = true

Agent: "That's everything — thanks! 🎉
        Here's your AED 20 Amazon gift card:
        https://reward.mesh.ai/gc/amzn20
        Enjoy!"
```

### Step 6: Completion

- Conversation status → `completed`
- Campaign `completed_conversations` incremented
- User demographics updated if any were collected
- User status → `onboarded` (if was new)
- When all conversations in the campaign are done, campaign status → `completed`

### Step 7: Data extraction

```
GET /campaigns/{id}/extractions

{
  "total_completed": 127,
  "extractions": [
    {
      "phone_number": "+971501234567",
      "data": {
        "current_station": "ADNOC, highway near Yas Island",
        "visit_frequency": "twice a week",
        "satisfaction": 7,
        "switch_reason": "closer location with car wash",
        "monthly_spend": "500-600 AED"
      }
    },
    ...
  ]
}
```

---

## Concurrency & Scale

**Thousands of conversations at once.** Each conversation is independent. The agent builds a fresh prompt per message from the conversation's own state.

**Single WhatsApp thread per user.** One conversation active at a time. Users can always be targeted for new campaigns, but bounty notifications are held while a side quest is active — they arrive the moment the current one finishes.

**Fast webhook response.** Twilio gets a 200 in < 100ms. All processing (LLM call, DB writes, Twilio send) happens in a background task.

**Rate limiting:**
- Outreach worker sends bounties at ~10/minute (configurable) to stay within Twilio limits
- LLM calls capped at 20 concurrent (configurable) via asyncio semaphore
- PostgreSQL advisory locks prevent race conditions per conversation

**No data loss.** Every message is persisted before any processing. If the LLM call fails, the message is saved and the next inbound message triggers a retry with full history.

---

## Stack

| Layer | Technology |
|-------|------------|
| **API** | Python 3.12, FastAPI, uvicorn |
| **Agent** | PydanticAI, Google Gemini 2.5 Flash |
| **Messaging** | Twilio WhatsApp API |
| **Database** | Neon PostgreSQL (shared with web app) |
| **DB Driver** | asyncpg (Python), Drizzle ORM (Next.js web app) |
| **Schema** | Defined in Drizzle, pushed via `db:push`, Python uses raw SQL |
| **Deploy** | Fly.io (backend), Vercel (web app) |

---

## What's Not in V1

- **Voice messages** — Users naturally send voice notes on WhatsApp. Supporting this is crucial — it removes friction and lets people respond how they're comfortable. Implementation: Twilio delivers voice messages as media URLs, we transcribe via Whisper or Gemini's audio input, and feed the transcript to the agent as if it were text. The user never knows the difference. This is a high-priority V2 feature.
- **Targeting from the pool** — V1 requires phone numbers per campaign. Auto-matching by demographics ("send this to all males 25-34 in Abu Dhabi") is a natural next step.
- **Reward fulfillment** — V1 sends a link. Actual gift card generation/payment integration comes later.
- **Analytics dashboard** — V1 has a raw extraction endpoint. Visual reports come later.
- **Multi-language** — V1 is English. The agent could handle Arabic naturally, but prompt tuning is needed.
- **User app/portal** — V1 is WhatsApp only. A web portal where users see their earnings, past bounties, etc. comes later.
