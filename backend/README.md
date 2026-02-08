# MeshAI Backend — Goal-Driven WhatsApp Research Agent

An autonomous conversational agent that conducts research interviews over WhatsApp with thousands of people simultaneously. Unlike a traditional survey bot that repeats fixed questions, this agent has a research goal and an extraction schema — it decides what to ask, how to ask it, and when the conversation is done.

## How It Works

```
Researcher                        Backend                         Participants
    │                                │                                │
    │  POST /campaigns               │                                │
    │  (brief + schema + phones)     │                                │
    │──────────────────────────────>│                                │
    │                                │                                │
    │  POST /campaigns/{id}/launch   │                                │
    │──────────────────────────────>│                                │
    │                                │   Opening messages (staggered) │
    │                                │──────────────────────────────>│
    │                                │                                │
    │                                │   Replies come in via Twilio   │
    │                                │<──────────────────────────────│
    │                                │                                │
    │                                │   Agent decides next question  │
    │                                │   based on what's missing      │
    │                                │──────────────────────────────>│
    │                                │                                │
    │                                │   ... natural conversation ... │
    │                                │                                │
    │                                │   Agent decides it's done      │
    │                                │   sends goodbye, marks complete│
    │                                │                                │
    │  GET /campaigns/{id}/extractions                                │
    │──────────────────────────────>│                                │
    │  ← structured data from all conversations                      │
```

**Per conversation, the agent:**
1. Receives the research brief and a schema of data points to extract
2. Sees the full conversation history and what data has been collected so far
3. Decides what to ask next — no script, no fixed question order
4. Extracts data points from each reply and tracks progress
5. Ends the conversation when all data points are collected

## UX — What the Participant Experiences

The person on the other end of WhatsApp never sees a form, a numbered list, or a robotic script. The experience feels like chatting with a curious, friendly researcher.

**Opening message** — The agent introduces itself, explains it's doing a quick research chat, and opens with something easy and non-threatening. No walls of text.

**During the conversation:**
- Messages are short: 1-3 sentences, WhatsApp-native tone
- The agent acknowledges what the person said before changing topics ("That's interesting — so you drive through there daily?")
- Natural transitions between topics, not abrupt pivots
- If someone gives a vague answer, the agent probes deeper before moving on
- If someone seems uncomfortable, the agent backs off gracefully
- The agent never reveals it has a checklist or specific data points to collect — it just feels like a conversation

**Ending** — When the agent has everything it needs, it sends a warm thank-you and ends naturally. No "Survey complete! Your reference number is..."

**Opt-out** — Sending "stop", "quit", "cancel", or "end" at any point immediately ends the conversation with a polite goodbye. No further messages are sent.

**What makes this different from a survey bot:**

| Survey Bot | MeshAI Agent |
|---|---|
| "Question 1 of 7: What is your age?" | "Hey! Quick question — what part of town do you usually commute from?" |
| Fixed question order | Agent decides order based on conversation flow |
| Ignores context from previous answers | Builds on what the person already said |
| Same script for everyone | Each conversation is unique |
| Hard cutoff at question N | Agent decides when it has enough |

## Stack

- **Python 3.12 + FastAPI** — async API server
- **PydanticAI + Gemini 2.5 Flash** — goal-driven conversational agent
- **Twilio** — WhatsApp message send/receive
- **Neon PostgreSQL** — shared database (same DB as the Next.js web app)
- **asyncpg** — async Postgres driver with connection pooling
- **Fly.io** — deployment

## Setup

### 1. Install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in:

```bash
cp .env.example .env
```

**Required:**

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_WHATSAPP_FROM` | Twilio WhatsApp sender (e.g. `whatsapp:+14155238886` for sandbox) |
| `GEMINI_API_KEY` | Google Gemini API key |

**Optional:**

| Variable | Default | Description |
|----------|---------|-------------|
| `OUTREACH_RATE_PER_MINUTE` | `10` | How many opening messages to send per minute |
| `MAX_CONCURRENT_LLM_CALLS` | `20` | Max parallel Gemini API calls |

### 3. Push the database schema

The schema is defined in `apps/web/db/schema.ts` (Drizzle ORM) and shared with the web app:

```bash
cd apps/web
pnpm db:push
```

### 4. Set up the Twilio webhook

Point your Twilio WhatsApp sender's incoming message webhook to:

```
POST https://<your-domain>/twilio/inbound
```

For local dev, use ngrok:

```bash
ngrok http 8000
# Then set Twilio webhook to: https://<ngrok-id>.ngrok.io/twilio/inbound
```

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

On startup, the server:
- Connects to PostgreSQL (asyncpg pool)
- Starts the outreach background worker (polls every 5s for pending sends)

## API

### Campaigns

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/campaigns` | Create a campaign |
| `GET` | `/campaigns` | List all campaigns |
| `GET` | `/campaigns/{id}` | Campaign detail + stats |
| `POST` | `/campaigns/{id}/launch` | Start staggered outreach |
| `POST` | `/campaigns/{id}/pause` | Pause pending outreach |

### Conversations & Data

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/campaigns/{id}/conversations` | List conversations + statuses |
| `GET` | `/conversations/{id}` | Full conversation with message history |
| `GET` | `/campaigns/{id}/extractions` | All extracted data from completed conversations |

### Webhooks

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/twilio/inbound` | Twilio WhatsApp incoming message webhook |

### Utility

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |

## Creating a Campaign

```bash
curl -X POST http://localhost:8000/campaigns \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Gas station feasibility - Yas Island",
    "research_brief": "We want to understand refueling habits of commuters who pass through Yas Island daily. We are evaluating whether to open a new gas station on the east side of the island.",
    "extraction_schema": {
      "age_range": {
        "type": "string",
        "description": "Age bracket, e.g. 25-34"
      },
      "commute_frequency": {
        "type": "string",
        "description": "How often they drive through Yas Island per week"
      },
      "current_station": {
        "type": "string",
        "description": "Where they currently refuel"
      },
      "satisfaction": {
        "type": "number",
        "description": "1-10 satisfaction with current fueling options"
      },
      "switch_reason": {
        "type": "string",
        "description": "What would make them switch to a new station"
      }
    },
    "phone_numbers": ["+971501234567", "+971509876543"]
  }'
```

Then launch it:

```bash
curl -X POST http://localhost:8000/campaigns/<campaign_id>/launch
```

The outreach worker will send opening messages at ~10/minute. As people reply, the agent carries each conversation independently.

## Database Schema

Five tables in the shared Neon PostgreSQL database:

| Table | Purpose |
|-------|---------|
| **users** | One row per unique phone number. No PII — just an identity key to track a person across campaigns. |
| **campaigns** | Research brief, extraction schema (what data to collect), phone list, status, completion counters. |
| **conversations** | One per user per campaign. Links to both `users` and `campaigns`. Holds `extracted_data` JSONB that accumulates as the agent talks. |
| **messages** | Full conversation transcript — every message sent and received, with timestamps and Twilio SIDs. |
| **outreach_queue** | Staggered outbound message scheduling. The background worker polls this table. |

Schema is defined in `apps/web/db/schema.ts` and pushed via Drizzle. The Python backend reads/writes the same tables using asyncpg raw queries.

### Conversation State Machine

```
pending → outreach_sent → active → completed
                                  → abandoned (user said "stop")
                       → failed   (send error)
```

### Campaign State Machine

```
draft → active → completed (all conversations done)
              → paused    (researcher paused)
```

## Concurrency Model

Designed to handle thousands of simultaneous conversations:

- **Inbound webhook** returns 200 immediately; processing happens in a background task
- **asyncio.Semaphore** caps concurrent LLM calls (default 20) to respect Gemini rate limits
- **PostgreSQL advisory locks** per conversation prevent race conditions from duplicate Twilio webhooks
- **FOR UPDATE SKIP LOCKED** in the outreach worker prevents double-sends
- **asyncpg connection pool** (2-10 connections) stays within Neon's limits

## Deployment (Fly.io)

```bash
cd backend

# Set secrets
fly secrets set DATABASE_URL="postgresql://..."
fly secrets set TWILIO_ACCOUNT_SID="AC..."
fly secrets set TWILIO_AUTH_TOKEN="..."
fly secrets set TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"
fly secrets set GEMINI_API_KEY="..."

# Deploy
fly deploy
```

The `fly.toml` is configured with `min_machines_running = 1` so the outreach background worker stays alive.

## Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app — campaign CRUD, Twilio webhook, inbound processing |
| `app/conversation_agent.py` | Goal-driven PydanticAI agent — builds dynamic system prompts, calls Gemini |
| `app/outreach_worker.py` | Background worker — polls outreach queue, generates + sends opening messages |
| `app/models.py` | Pydantic request/response models (`CreateCampaignRequest`, `AgentResponse`) |
| `app/db.py` | asyncpg connection pool lifecycle |
| `app/config.py` | Environment variable loading |
| `app/twilio_client.py` | Twilio WhatsApp send wrapper |
| `app/analytics_agent.py` | AI report generation (kept from previous version, adapt later) |
| `app/tsx_safety.py` | TSX validation for generated reports |
