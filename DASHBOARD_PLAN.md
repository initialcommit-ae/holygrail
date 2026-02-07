# Dashboard MVP — Frontend Demo Plan

## Overview

Build a **frontend-first** `/dashboard` for creating surveys via a conversational chat (Gemini). For demo, everything runs in the browser and Next.js API routes; the only backend call is **POST /start** with a list of questions (matching current backend).

**In scope for MVP:**
- Sidebar: Create new survey, View past surveys, Your conversation
- Chat with AI to describe objective and extract demographics (Gemini)
- Mock respondent match count (no DB)
- AI-generated survey questions; user can review/edit
- Mock cost summary
- **Start** → call backend `POST /start` with `questions` only

**Out of scope for MVP (later):**
- Real DB respondent matching, study/brief/conversation records
- Auth (use hardcoded or none for demo)

---

## Backend Contract (Current)

The FastAPI backend has a single endpoint the dashboard needs:

**POST** `{BACKEND_API_URL}/start`

**Request:**
```json
{ "questions": ["Question 1?", "Question 2?", ...] }
```

**Response:**
```json
{ "ok": true, "sent_to": "whatsapp:+971...", "question_count": 5 }
```

- Backend uses **file-based state** (no DB). It sends the first question to a hardcoded WhatsApp number (Twilio).
- No studyId, respondentIds, or demographics are sent; only `questions` matter.

---

## User Flow (Demo)

```
1. User describes survey objective in chat
   ↓
2. AI asks clarifying questions (age, location, occupation)
   ↓
3. App shows mock "matching respondent" count (e.g. from static JSON or fixed number)
   ↓
4. AI generates 10–15 survey questions
   ↓
5. User reviews/edits questions
   ↓
6. App shows mock cost breakdown → "How many respondents?"
   ↓
7. User confirms → Call backend POST /start with questions → Show success
```

---

## Architecture (MVP)

```
┌─────────────────────────────────────────────────────────┐
│  Dashboard (apps/web)                                   │
│  ┌─────────────┐  ┌──────────────────────────────────┐ │
│  │ Sidebar     │  │ Chat + Demographics + Questions  │ │
│  │ • New       │  │ • Message history (React state)  │ │
│  │ • Past      │  │ • Demographics summary           │ │
│  │ • Convo     │  │ • Question editor                │ │
│  └─────────────┘  │ • Mock match count & cost         │ │
│                  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
        │
        ├── Next.js API routes (Gemini only for MVP)
        │   • /api/chat        → Gemini conversation + demographics extraction
        │   • /api/survey/generate → Gemini question generation
        │   • /api/survey/start    → Proxy to backend POST /start (questions only)
        │
        └── Optional: /api/respondents/match → returns mock count (no DB)
```

---

## Dependencies

```bash
cd apps/web
pnpm add @google/generative-ai zod clsx tailwind-merge
```

- `@google/generative-ai` — Gemini
- `zod` — Validate AI/output schemas
- `clsx` + `tailwind-merge` — Class merging (or use existing `cn` if present)

---

## Environment Variables

In `apps/web/.env.local`:

```bash
# Gemini (required for chat + question generation)
GOOGLE_GEMINI_API_KEY="your-gemini-api-key"
# or GEMINI_API_KEY (backend uses this name)

# Backend (for Start survey)
BACKEND_API_URL="http://localhost:8000"
```

---

## File Structure (Trimmed)

```
apps/web/
├── app/
│   ├── dashboard/
│   │   └── page.tsx              # Dashboard layout + sidebar + main area
│   └── api/
│       ├── chat/
│       │   └── route.ts          # Gemini chat + demographics extraction
│       ├── respondents/
│       │   └── match/
│       │       └── route.ts      # Mock match count (JSON, no DB)
│       └── survey/
│           ├── generate/
│           │   └── route.ts      # Gemini question generation
│           └── start/
│               └── route.ts      # Forward to backend POST /start
│
├── components/
│   ├── dashboard/
│   │   ├── ChatInterface.tsx     # Chat UI + message list
│   │   ├── ChatMessage.tsx       # Single message bubble
│   │   ├── DemographicsSummary.tsx
│   │   ├── RespondentMatcher.tsx  # Shows "X respondents match" (mock)
│   │   ├── QuestionEditor.tsx    # List of questions, add/remove/edit
│   │   └── BillingConfirmation.tsx # Mock cost + confirm → Start
│   └── ui/                       # Only if not in packages/ui
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Card.tsx
│       └── Badge.tsx
│
├── lib/
│   ├── gemini/
│   │   ├── client.ts
│   │   ├── prompts.ts
│   │   └── types.ts              # Zod schemas for demographics / extraction
│   ├── backend/
│   │   └── client.ts             # Single function: startSurvey(questions)
│   └── utils/
│       └── cn.ts
│
└── types/
    ├── chat.ts
    └── survey.ts                 # Questions, demographics, start payload
```

**Omitted for MVP:** `lib/db/queries.ts`, `lib/db/mutations.ts`, real DB in respondent match, cost calculator (can be inline mock).

---

## Implementation Phases

### Phase 1: Foundation
- `lib/utils/cn.ts`
- UI: Button, Input, Card, Badge (or reuse from `packages/ui`)
- Types: `types/chat.ts`, `types/survey.ts`

### Phase 2: Chat + Gemini
- `lib/gemini/client.ts`, `lib/gemini/prompts.ts`, `lib/gemini/types.ts`
- `app/api/chat/route.ts`
- `components/dashboard/ChatMessage.tsx`, `ChatInterface.tsx`

### Phase 3: Demographics + Mock Match
- `app/api/respondents/match/route.ts` — return mock `{ count, tierDistribution }` (e.g. from a static JSON or random)
- `DemographicsSummary.tsx`, `RespondentMatcher.tsx`

### Phase 4: Questions
- `app/api/survey/generate/route.ts`
- `QuestionEditor.tsx`

### Phase 5: Start Survey
- `lib/backend/client.ts` — `startSurvey(questions)` → POST to `BACKEND_API_URL/start`
- `app/api/survey/start/route.ts` — receive `{ questions }`, call backend, return `{ ok, sent_to, question_count }`
- `BillingConfirmation.tsx` — mock cost, confirm, then call `/api/survey/start`

### Phase 6: Dashboard Page
- `app/dashboard/page.tsx` — sidebar + main area wiring all components

---

## API Contracts (MVP)

### POST `/api/chat`
**Request:** `{ messages: Array<{ role: "user" | "assistant", content: string }> }`  
**Response:** `{ message: string, demographics?: {...}, ready?: boolean }`

### POST `/api/respondents/match`
**Request:** `{ demographics: { ageRange?, location?, occupation? } }`  
**Response:** `{ count: number, tierDistribution?: {...} }` — **mock for MVP**

### POST `/api/survey/generate`
**Request:** `{ objective: string, demographics?: object }`  
**Response:** `{ questions: string[] }`

### POST `/api/survey/start`
**Request:** `{ questions: string[] }`  
**Response:** `{ ok: boolean, sent_to?: string, question_count?: number }` — mirrors backend.

---

## UI/UX (Match Current Site)

- Reuse marketing style: black buttons, rounded-full, font-mono where appropriate, slate/white.
- Sidebar: simple list (Create new survey, View past surveys, Your conversation).
- Chat: WhatsApp-like bubbles; AI left, user right.
- Progressive: show demographics and match count when available; then questions; then mock cost and Start.

---

## Success Criteria (Demo)

- User can describe a survey in chat and get demographics extracted via Gemini.
- User sees a (mock) respondent count and AI-generated questions, and can edit questions.
- User sees a (mock) cost and clicks Start; backend receives POST /start with the chosen questions and first message is sent to WhatsApp (or backend returns success).

---

## Later (Post-MVP)

- Real respondent matching from `apps/web/db` (Drizzle + `respondents.declaredAttrs`).
- Create study/brief/conversation records in DB before or after calling backend.
- Auth (e.g. Clerk), past surveys list from DB, real cost calculation by tier.
