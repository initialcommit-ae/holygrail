# MeshAI — Complete Product & Technical Specification
### Autonomous Market Intelligence

**Version:** 1.0
**Date:** February 7, 2026
**Authors:** Andrés, Moudja, Ashok

---

## Part 1: The Problem

Every significant decision — building a gas station, launching a product line, changing a government policy, opening a restaurant — is fundamentally a bet. The quality of that bet depends on the quality of information behind it.

Right now, there are two ways to get that information from real people:

**The cheap way.** Blast a Google Form or SurveyMonkey link. You get volume but garbage quality. People click through mindlessly. You get what people think you want to hear, not what they actually think. The questions are designed by someone who may not know research methodology. The respondents are whoever happens to click the link — not the people whose opinions actually matter for your decision. And you get structured data (1-5 ratings) but no depth. You know *what* people think but not *why*.

**The expensive way.** Hire a consultancy. They design a proper research methodology, recruit qualified respondents, send trained interviewers to have real conversations, then analysts spend weeks synthesizing findings into a report. The output is excellent — nuanced, actionable, defensible. But it costs tens of thousands of dollars, takes weeks to months, and is therefore only accessible to organizations with serious budgets. The Indian restaurant will never hire McKinsey.

These are the only two options because **the work of designing good questions, finding the right people, having meaningful conversations, and synthesizing insights has always required expensive humans at every step.**

That structural constraint is gone.

But simply replacing each human with an AI agent isn't enough. The deeper problem is that the entire survey paradigm is flawed. Surveys are adversarial by design — the researcher wants truth, the respondent wants to finish quickly (or get paid). The format itself (structured questions with predefined answers) compresses human experience into boxes that are convenient for analysis but lossy for insight.

What actually produces insight is conversation. When a skilled interviewer asks someone about their commute and the person talks for two minutes about how they rearranged their morning because the gas station on their route closed, that contains more signal than 50 people rating "gas station accessibility" on a 1-5 scale. The problem is that conversations don't scale and they're expensive to analyze.

Until now.

The real problem isn't "surveys are expensive" — it's that **the relationship between the quality of human insight and the cost to obtain it has always been linear, and that has made real market intelligence inaccessible to most decision-makers.**

---

## Part 2: The Product

### 2.1 What MeshAI Is

MeshAI is an autonomous market intelligence system. A business describes a decision they're trying to make. The system figures out what it needs to learn from which people, conducts those conversations via WhatsApp, and delivers actionable intelligence — not raw data, not bar charts, but the kind of synthesized, defensible insight that a consultancy would deliver.

### 2.2 The Two Sides

**Demand side.** Businesses and institutions that need to understand what people think, feel, experience, and want in order to make better decisions. From a government ministry planning rail infrastructure to a restaurant owner considering a new location.

**Supply side.** A population of respondents who are compensated for sharing their perspectives through conversational interactions on WhatsApp. No app download. No account creation. No digital literacy barrier.

### 2.3 The Three Agents

Three AI agents bridge these sides, performing work that previously required three expensive humans:

**The Research Designer** takes a business objective and works backward to figure out what information would actually de-risk that decision. It doesn't design a questionnaire — it produces a research brief: a set of information objectives that tell the Field Agent what to go learn, from whom, and how to know when it has enough.

**The Field Agent** conducts adaptive, conversational interviews over WhatsApp. It doesn't follow a script. It has a checklist of things to learn and uses professional interviewing techniques to learn them through natural conversation. People who feel heard give honest, detailed answers.

**The Analyst** takes unstructured conversational data from dozens of field interactions, identifies patterns, resolves contradictions, segments by demographics, and synthesizes everything into an executive intelligence brief — the deliverable that the business actually needs to make their decision.

### 2.4 Why WhatsApp

For the UAE specifically, WhatsApp is the universal interface — already on every phone, across every demographic, nationality, and income level. A construction worker in Al Ain and a C-suite executive in DIFC both interact the same way: a WhatsApp message arrives, they have a conversation, they get paid. No app store. No friction.

---

## Part 3: User Journeys

### 3.1 The Business Journey

**Step 1: Describe the objective.** The business interacts with the Research Designer through the web dashboard. This is a conversation, not a form. They describe what they're trying to decide. The Research Designer asks clarifying questions: What's the context? What do you already know? Who are the people whose perspectives matter most? What would change your decision? The business can provide supporting materials — internal documents, prior research, market data.

**Step 2: Review the research brief.** The Research Designer produces a research brief: information objectives, respondent targeting criteria, sensitive areas, completion criteria. The business reviews this as an interactive artifact — they can see each element, understand why it's there, and adjust it.

**Step 3: Approve and deploy.** The system matches respondents from the pool against targeting criteria and begins deploying conversations. The business sees: how many respondents were matched, how many conversations are in progress, how many are complete.

**Step 4: Monitor in real-time.** As conversations complete, the business sees response rates, completion rates, and emerging themes. Early signal. Enough to see if the study is on track.

**Step 5: Receive the intelligence brief.** When the study reaches its completion criteria, the Analyst generates the intelligence brief. Executive summary, findings, demographic breakdowns, confidence levels, tensions, and recommendations.

**Step 6: Query and explore.** The business asks follow-up questions. The Analyst answers from the underlying data. The data doesn't expire.

### 3.2 The Respondent Journey

**Step 1: Onboarding.** A person texts a WhatsApp number or scans a QR code. A brief, friendly conversation collects basic demographics: age range, gender, nationality, general location, occupation category. No name. No ID. The tone: "You'll receive conversation opportunities from time to time. Each one pays [X]. You can always say no."

**Step 2: Wait for a match.** When a study's targeting criteria match their profile, they receive a WhatsApp message: brief description of the opportunity, estimated time, compensation. Accept or decline. No penalty for declining.

**Step 3: Have the conversation.** The Field Agent conducts the interview in the same WhatsApp thread. Conversational, adaptive, respectful. The respondent answers at their own pace — they can pause, come back later, pick up where they left off.

**Step 4: Get compensated.** When complete, compensation is credited. They can check balance, see history, and redeem via WhatsApp commands.

**Step 5: Build a profile over time.** Each conversation enriches the system's understanding. After 10 conversations across different studies, the system knows commute patterns, shopping habits, family situation, pain points — all derived from natural conversation. Better matching, more relevant opportunities. This is the retention loop.

### 3.3 The Study Lifecycle

```
Business describes objective
        │
        ▼
Research Designer produces research brief
        │
        ▼
Business reviews and approves
        │
        ▼
System matches respondents from pool
        │
        ▼
Matched respondents receive WhatsApp invitation
        │
        ▼
Accepting respondents connected to Field Agent
        │
        ▼
Field Agent conducts adaptive conversations
        │
        ▼
Each completed conversation → structured extraction
        │
        ▼
Study monitor checks completion criteria
        │
        ▼
Analyst synthesizes all extractions into intelligence brief
        │
        ▼
Business receives brief + queryable data layer
```

---

## Part 4: The Three Agents — Detailed Specification

### 4.1 Research Designer Agent

**Role.** Research strategist. Not a survey designer. Its job is to answer: "What do we need to learn — and from whom — to de-risk this decision?"

**Input.** Business objective (natural language), context documents, answers to clarifying questions, budget tier.

**Core capabilities:**

*Decision decomposition.* Takes a vague business objective and decomposes it into specific, testable information needs using the SCQ framework (Situation-Complication-Question), MECE decomposition (Mutually Exclusive, Collectively Exhaustive), and issue trees. Every terminal node maps to a specific information need that can be addressed through conversation.

*Hypothesis-driven research.* Forms an initial hypothesis before designing research. "A gas station on Yas Island will achieve profitability within 18 months because daily traffic exceeds 15,000 vehicles and the nearest competitor is 8km away." Research is designed to prove or disprove specific claims.

*Assumption mapping.* Identifies what needs to be true for the business idea to work. Categorizes assumptions as Desirability, Feasibility, Viability, Adaptability. Prioritizes high-importance, low-evidence assumptions for research.

*Value of information assessment.* Determines whether research is justified. If no plausible finding would change the decision, the research is not worth conducting.

*80/20 principle.* Only gathers information sufficient for roughly 80% confidence. Resists scope creep.

**Output: The Research Brief.** This is the handoff document to the Field Agent. It contains exactly what the Field Agent needs, nothing it doesn't.

```json
{
  "decision_context": "2-3 sentences. What decision is being made and why.",

  "information_objectives": [
    {
      "id": "obj_1",
      "label": "Current refueling patterns",
      "description": "Where, how often, how far they travel, why they chose their station",
      "what_good_looks_like": "Specific behavioral data: station names, frequency per week, drive times. Not just attitudes.",
      "priority": 1
    }
  ],

  "targeting": {
    "must_have": ["Lives on or within 5km of Yas Island", "Owns or regularly uses personal vehicle"],
    "nice_to_have": ["Mix of ages", "Range of income levels"],
    "quotas": [
      { "segment": "Daily commuters through Yas", "min": 8 },
      { "segment": "Yas Island residents", "min": 5 }
    ]
  },

  "sensitive_areas": [
    "Don't reveal client is an oil company",
    "Don't ask willingness-to-pay directly — explore actual spending behavior"
  ],

  "completion_criteria": {
    "min_conversations": 30,
    "quota_requirements": "all quotas filled",
    "objective_coverage": "all priority-1 objectives covered by 20+ respondents"
  },

  "priority_ranking": ["obj_1", "obj_2", "obj_3", "obj_4"]
}
```

### 4.2 Field Agent

**Role.** Qualitative interviewer conducting adaptive, semi-structured conversations over WhatsApp. Has information objectives, not a script. Knows what to learn, not what to say.

**Input.** Research brief (from Designer), respondent profile, full conversation history (grows with each message).

**Core capabilities:**

*Open-ended interviewing.* Every topic approached with questions that let the respondent tell their story. "Walk me through what your typical morning looks like" not "Do you drive to work?" The goal is hearing what respondents think is important in their own words.

*Probing for depth.* Uses the DICE framework — Descriptive probes ("Can you describe what that looked like?"), Idiographic probes ("Can you think of a specific time?"), Clarifying probes ("What do you mean by 'inconvenient'?"), Explanatory probes ("Why do you think that is?"). Descriptive and idiographic early (rapport building). Clarifying and explanatory later (after trust established).

*Rapport building.* Mirrors respondent communication style. Starts with easy, non-threatening topics. Acknowledges every significant response before asking the next question. Avoids transactional question-answer patterns. Conversations should feel like "texting with a curious, friendly person who wants to understand your perspective."

*Indirect elicitation.* Behavioral questions over attitudinal ones. Narrative elicitation ("Walk me through your last grocery run" reveals car ownership, store preferences, spending patterns, family size without asking about any directly). Laddering technique (probe from preference → consequence → underlying value). Contradiction detection without confrontation.

*Objective tracking.* Maintains a running assessment of which information objectives from the brief have been satisfied. Uses natural transitions to move to uncovered objectives. Knows when to stop. Doesn't ask filler questions.

**Output: Per-message response.**

```json
{
  "message": "That's really interesting — so you're driving past Yas Mall every morning. What does your fuel situation usually look like along that route?",
  "objective_tracker": {
    "obj_1": { "status": "in_progress", "notes": "Established commute route, probing refueling" },
    "obj_2": { "status": "not_started", "notes": "" }
  },
  "internal_notes": "Respondent is talkative. Mentioned kids — possible family commute pattern.",
  "conversation_status": "continue",
  "derived_attrs_observed": ["has_children", "daily_commuter", "passes_yas_mall"]
}
```

**Output: Structured extraction (on conversation completion).**

```json
{
  "respondent_profile_enriched": {
    "declared": { "age_range": "30-40", "gender": "male", "area": "Al Reem Island" },
    "derived": {
      "has_children": true,
      "commute_pattern": "daily, Al Reem → Yas Island via E10",
      "vehicle_ownership": true,
      "current_fuel_station": "Emirates, Saadiyat",
      "fuel_frequency": "2x per week"
    }
  },
  "objective_coverage": {
    "obj_1": {
      "status": "covered",
      "summary": "Refuels 2x/week at Emirates Saadiyat. 12-min detour. Monday and Thursday mornings."
    },
    "obj_2": {
      "status": "covered",
      "summary": "Strong frustration with wait times 7-8am. Estimates 10-15 min waits. Late to school pickup as result."
    }
  },
  "unexpected_findings": [
    "Three neighbors recently bought EVs. No charging infrastructure on island."
  ],
  "confidence_flags": {
    "overall": "high",
    "notes": "Detailed, consistent, specific throughout. No signs of gaming."
  }
}
```

### 4.3 Analyst Agent

**Role.** Qualitative synthesis specialist. Takes all conversation data and produces an actionable intelligence brief.

**Input.** All structured extractions, all raw transcripts, the research brief, study metadata.

**Core capabilities:**

*Thematic analysis.* Adapted from Braun & Clarke's six-phase framework: familiarization with data, coding, theme development, theme review, theme refinement, synthesis into brief. Themes make claims about what the data shows ("Morning refueling is a significant pain point driven by time pressure, not distance"), not just topic labels.

*Answer-first communication.* Pyramid Principle: lead with the conclusion, then supporting evidence. The executive summary is readable in 60 seconds.

*Confidence assessment.* Every finding accompanied by confidence level. High: consistent signal across demographics and conversational angles. Medium: supported by multiple respondents but single demographic or potential framing influence. Low: small numbers, contradicted by other evidence, thin data.

*Tension surfacing.* Real human opinion is messy. People say they want cheaper fuel but won't drive 5 extra minutes. The Analyst surfaces contradictions as real tensions the business must navigate, not data quality problems.

*Recommendations as options.* Not "build the gas station" but "three options worth considering, each connected to specific findings."

**Output: Intelligence Brief.**

```json
{
  "exec_summary": "2-3 paragraphs. What we learned and what the business should consider.",

  "findings": [
    {
      "id": "f1",
      "claim": "Morning commuters through Yas Island represent a captive, underserved market",
      "evidence": "22 of 30 respondents who commute through Yas described refueling detours of 10+ minutes...",
      "confidence": "high",
      "demographic_notes": "Consistent across age groups and income levels"
    }
  ],

  "demographic_breakdowns": [
    {
      "dimension": "Age",
      "finding": "Under-30s 3x more likely to mention EV charging as deciding factor",
      "significance": "Suggests hybrid fuel/charging format may be relevant for long-term viability"
    }
  ],

  "tensions": [
    {
      "tension": "Respondents want cheaper fuel but won't drive more than 5 minutes out of their way",
      "implication": "Location accessibility may matter more than price competitiveness"
    }
  ],

  "recommendations": [
    {
      "option": "Traditional station optimized for morning throughput in northern corridor",
      "supported_by": ["f1", "f2"],
      "tradeoff": "Captures current demand but may underserve emerging EV segment"
    }
  ],

  "methodology": {
    "conversations_completed": 30,
    "date_range": "Feb 5-7, 2026",
    "demographics_summary": "...",
    "known_gaps": "Limited representation of 45+ age group (3 respondents)"
  }
}
```

---

## Part 5: System Architecture

### 5.1 Overview

```
┌──────────────────────────────────────────────────────────────┐
│                       MeshAI PLATFORM                          │
│                                                              │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐          │
│  │  RESEARCH   │──▶│   FIELD    │──▶│  ANALYST   │          │
│  │  DESIGNER   │   │   AGENT    │   │   AGENT    │          │
│  └──────┬──────┘   └─────┬──────┘   └─────┬──────┘          │
│         │                │                │                  │
│         │          ┌─────┴──────┐         │                  │
│         │          │  WHATSAPP  │         │                  │
│         │          │  GATEWAY   │         │                  │
│         │          │  (Twilio)  │         │                  │
│         │          └─────┬──────┘         │                  │
│  ┌──────┴────────────────┴───────────────┴──────┐           │
│  │              CORE DATABASE (Supabase)         │           │
│  └───────────────────────────────────────────────┘           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ BUSINESS UI  │  │ STUDY MONITOR│  │ MATCHING     │       │
│  │ (Next.js)    │  │ (background) │  │ ENGINE       │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 Agent Orchestrator

The orchestrator manages the lifecycle of agent invocations. Each agent is a Claude API call with a specialized system prompt and structured JSON output.

**Designer Invocation.** Triggered when a study is created with business context. Input: study objective + context. System prompt: Designer KB. Output: research brief → stored in DB as structured JSON. Business reviews and approves.

**Field Agent Invocation.** One per inbound message. Triggered when a respondent sends a WhatsApp message. Input: research brief + respondent profile + full conversation history. System prompt: Field Agent KB. Output: next message → Twilio → WhatsApp. On conversation completion: triggers extraction (a separate Claude call that produces the structured extraction from the full transcript).

**Analyst Invocation.** Triggered when study completion criteria are met. Input: all structured extractions + raw transcripts + research brief + study metadata. System prompt: Analyst KB. Output: intelligence brief → stored in DB.

**Query Invocation.** Triggered when business asks a follow-up question. Input: question + intelligence brief + relevant extractions. Output: answer → UI.

### 5.3 The Field Agent Message Loop

```
Respondent sends WhatsApp message
        │
        ▼
Twilio webhook receives message → /api/twilio/webhook
        │
        ▼
Route to active conversation (lookup by phone number)
        │
        ▼
Append message to messages table
        │
        ▼
Build LLM context:
  System prompt = Field Agent KB + research brief + respondent profile + objective tracker
  Messages = full conversation history
        │
        ▼
Claude API call → returns JSON:
  { message, objective_tracker, internal_notes, conversation_status, derived_attrs }
        │
        ▼
Store agent message + metadata in DB
        │
        ▼
Send message via Twilio to WhatsApp
        │
        ▼
If conversation_status = "complete":
  → Trigger extraction (separate Claude call on full transcript)
  → Update respondent derived profile
  → Mark conversation complete
  → Trigger compensation
  → Update study progress
```

### 5.4 WhatsApp Gateway (Twilio)

**Outbound.** Agent orchestrator → Twilio API → WhatsApp. Two message types: template messages (for invitations, pre-approved by WhatsApp) and session messages (within 24hr window after user's last message).

**Inbound.** WhatsApp → Twilio webhook → /api/twilio/webhook. Route to correct conversation. Append to message history. Trigger Field Agent for next response.

**Session management.** Twilio 24hr session window. If respondent goes silent and returns after 24hr, re-engage with template message. Message queuing for rate limits.

### 5.5 Study Monitor

Background process (cron or event-driven) that:

- Tracks study progress against completion criteria
- Monitors quota fill rates
- Detects stalled conversations (no response in X hours)
- Triggers additional invitations if response rate too low
- Triggers Analyst when completion criteria met
- Sends progress updates to business dashboard via Supabase Realtime

### 5.6 Matching Engine

Takes targeting criteria from the research brief and finds the right respondents.

Process:
1. Filter respondent pool by must-have criteria
2. Score candidates by: match quality (declared + derived attrs), reliability score (past consistency), availability (not in active conversation), recency (not contacted recently)
3. Select candidates to fill quota requirements
4. Generate personalized invitation messages
5. Send invitations via WhatsApp gateway

---

## Part 6: Database Schema

### Core Tables

**businesses**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| name | text | |
| email | text | |
| plan_tier | text | |
| created_at | timestamp | |

**studies**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| business_id | uuid FK → businesses | |
| objective_text | text | Raw business input |
| context | text | Additional context provided |
| status | enum | draft, review, approved, field, analysis, done |
| study_type | enum | quick_pulse, standard, deep_dive |
| budget_tier | text | |
| created_at | timestamp | |
| completed_at | timestamp | |

**research_briefs**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| study_id | uuid FK → studies | |
| version | int | Supports iterations |
| decision_context | text | |
| info_objectives | jsonb | Array of objective objects |
| targeting | jsonb | Criteria + quotas |
| sensitive_areas | jsonb | |
| completion_criteria | jsonb | |
| priority_ranking | jsonb | |
| approved_at | timestamp | |

**respondents**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| phone_hash | text | Hashed phone number (privacy) |
| whatsapp_id | text | For Twilio routing |
| declared_attrs | jsonb | From onboarding |
| derived_attrs | jsonb | From conversations |
| reliability_score | float | 0-1, starts at 0.5 |
| consistency_score | float | Cross-conversation consistency |
| total_convos | int | |
| tier | enum | community_voice, active_contributor, community_expert |
| earnings_total | decimal | |
| created_at | timestamp | |
| last_active | timestamp | |

**conversations**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| study_id | uuid FK → studies | |
| respondent_id | uuid FK → respondents | |
| status | enum | invited, accepted, active, complete, abandoned |
| started_at | timestamp | |
| completed_at | timestamp | |
| duration_seconds | int | |
| compensation_amt | decimal | |
| compensation_paid | boolean | |

**messages**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| conversation_id | uuid FK → conversations | |
| sender | enum | agent, respondent |
| content | text | Message body |
| metadata | jsonb | Objective tracker, internal notes (agent messages only) |
| timestamp | timestamp | |
| twilio_sid | text | For delivery tracking |

**extractions**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| conversation_id | uuid FK → conversations | One per completed conversation |
| respondent_profile | jsonb | Enriched from conversation |
| objective_coverage | jsonb | Per-objective status + summary |
| unexpected_findings | jsonb | |
| confidence_flags | jsonb | |
| derived_attrs_new | jsonb | New attributes discovered |
| created_at | timestamp | |

**intelligence_briefs**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| study_id | uuid FK → studies | |
| exec_summary | text | |
| findings | jsonb | Array of findings with confidence |
| demographics | jsonb | |
| tensions | jsonb | |
| recommendations | jsonb | |
| methodology | jsonb | Sample description, timeline |
| created_at | timestamp | |

**query_log**
| Column | Type | Notes |
|--------|------|-------|
| id | uuid PK | |
| study_id | uuid FK → studies | |
| business_id | uuid FK → businesses | |
| question | text | |
| answer | text | |
| sources_used | jsonb | Which extractions cited |
| created_at | timestamp | |

---

## Part 7: The Handoff Chain

The quality of the entire system depends on clean handoffs between agents. Each handoff has a specific contract:

```
Business Objective (natural language, vague)
    │
    ▼
RESEARCH DESIGNER produces:
    → Research Brief
      (decision context, information objectives with "what good looks like",
       targeting criteria, sensitive areas, completion criteria, priorities)
    │
    ▼
FIELD AGENT receives brief, conducts conversations, produces:
    → Per conversation:
      raw transcript + enriched respondent profile + objective coverage matrix
      + unexpected findings + confidence flags
    │
    ▼
ANALYST receives all conversation outputs, produces:
    → Intelligence Brief
      (exec summary, findings with confidence, demographics, tensions,
       recommendations, methodology)
    + Queryable data layer for follow-up questions
```

**Designer → Field Agent contract.** "Here is what you need to learn, from whom, and how you'll know you have enough. I've done the thinking about why these questions matter — you focus on how to get the answers through natural conversation."

**Field Agent → Analyst contract.** "Here is what each person told me, structured so you can see what we learned against each objective. I've flagged anything that seemed off. Raw transcripts are there if you need to go deeper."

**Analyst → Business contract.** "Here is what we found, how confident we are, and what you should consider doing. Ask me follow-up questions and I'll answer from the data."

---

## Part 8: The Qualification and Honesty Problem

### 8.1 The Incentive Misalignment

The platform pays people to participate. Some studies pay more than others. This creates an incentive to misrepresent to qualify for higher-paying studies.

### 8.2 Five-Layer Defense

**Layer 1: Indirect qualification.** The Research Designer builds information objectives that reveal qualification-relevant information indirectly. You don't ask "are you a lawyer" — the Field Agent asks "walk me through your typical workday" and a real lawyer's answer is unmistakably different.

**Layer 2: Derived profile matching.** Over time, the system has extensive derived knowledge about each respondent. If 10 conversations reveal someone is a student, the system won't match them to a study requiring practicing lawyers, regardless of what they declared.

**Layer 3: Consistency scoring.** Tracks consistency across a respondent's history. If claimed attributes shift dramatically between studies in implausible ways, their reliability score drops and they receive fewer high-value opportunities.

**Layer 4: Conversational verification.** The Field Agent can, within natural conversation flow, verify claimed attributes. If someone was matched based on prior car ownership mentions, the agent naturally references transportation early to reconfirm.

**Layer 5: Economic design.** Compensation rewards long-term reputation over short-term gain. A respondent with 50 studies and high consistency gets premium access. Gaming one study to earn an extra 20 AED isn't worth risking hundreds of future opportunities.

---

## Part 9: Privacy and Data Ethics

**Minimum necessary information.** No full names, email addresses, home addresses, or government ID collected. Phone number (inherent to WhatsApp) is the only PII, stored separately from conversational data.

**Data separation.** Business-side data and respondent-side data are architecturally separated. The business sees aggregated, anonymized intelligence. The respondent sees only their own conversations and earnings.

**PII stripping.** Before data reaches the Analyst or business, any personally identifiable information volunteered during conversation (names, specific addresses, employer names) is stripped.

**Right to deletion.** "Delete my data" in WhatsApp triggers a complete wipe of profile, conversation history, and derived attributes.

**Business confidentiality.** Businesses may share sensitive strategic information with the Research Designer. Never shared with respondents or third parties. Respondents never know which company commissioned the study unless explicitly disclosed.

---

## Part 10: Study Types

### Quick Pulse
3-5 information objectives. Short conversations (2-5 minutes). High volume. Fast turnaround (hours). The Field Agent is more direct, less conversational. The Analyst produces a summary rather than a full brief.

### Standard Study
6-15 information objectives. Conversational interviews of 5-15 minutes. Mix of behavioral and attitudinal signal. 30-200 respondents. Full intelligence brief.

### Deep Dive
15+ information objectives. Long-form interviews of 15-45 minutes, potentially across multiple sessions. Deep probing. Small but carefully targeted sample (10-50). Comprehensive report with persona-level insights and strategic recommendations.

---

## Part 11: Economic Model

```
Business pays per study → MeshAI takes margin → Respondents compensated per conversation
```

**Business pricing** is outcome-based, not per-message. Factors: study type, sample size, targeting specificity, turnaround time.

**Respondent compensation** scales with effort and expertise. Quick Pulse < Standard < Deep Dive. Professional expertise commands premium. High reliability scores unlock premium opportunities.

**The margin** funds the intelligence layer. The business pays far less than a consultancy. The respondent earns fair compensation. MeshAI's margin is the arbitrage on automating expensive human expertise.

---

## Part 12: Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Next.js 14 (App Router) | Business dashboard |
| Styling | Tailwind CSS | |
| Backend | Next.js API Routes / tRPC | |
| Database | Supabase (Postgres + Auth + Realtime) | |
| AI | Claude API (Anthropic) | 3 system prompts + structured JSON output |
| Messaging | Twilio WhatsApp Business API | Webhook inbound, REST outbound |
| Hosting | Vercel | |
| Payments | Stripe (business billing) | |
| Respondent payouts | Manual initially → automated later | |

---

## Part 13: Build Phases

### Phase 1: Foundation
- Supabase project + schema (all tables)
- Next.js project scaffold
- Twilio WhatsApp sandbox setup
- Claude API integration (basic call wrapper)
- Auth (Supabase Auth for business users)

### Phase 2: Agent Core
- Research Designer system prompt + invocation
- Field Agent system prompt + message loop
- Field Agent extraction prompt
- Analyst system prompt + invocation
- Agent orchestrator (lifecycle management)

### Phase 3: WhatsApp Integration
- Twilio webhook endpoint (inbound messages)
- Message routing (phone → conversation → agent)
- Outbound message sending
- Session management (24hr windows)
- Template messages for invitations

### Phase 4: Business UI
- Study creation flow (intake form / conversation)
- Research brief review + approval
- Study progress dashboard (real-time via Supabase Realtime)
- Intelligence brief display
- Queryable follow-up interface

### Phase 5: Operations
- Respondent pool management
- Matching engine
- Study monitor (progress + triggers)
- Compensation tracking
- Conversation monitoring (QA)

---

## Part 14: The Flywheel

Every component reinforces every other.

**More respondents** → better demographic coverage → better matching → higher data quality → more valuable to businesses.

**More businesses** → more opportunities → more earning potential → attracts more respondents.

**More conversations** → richer derived profiles → better qualification → less gaming → higher data quality.

**More completed studies** → more training signal for agents (what approaches produce the best data) → better methodology → higher quality.

**Higher data quality** → stronger reputation → premium pricing → higher respondent compensation → attracts better respondents.

The cold start: seed the respondent pool at universities (high density, low cost, lots of free time) and approach businesses with the existing pool as proof.

---

## Part 15: What Success Looks Like

**For the business.** "I described what I needed to know, reviewed a research plan in 10 minutes, and had a synthesized intelligence brief by the next morning. The insights were specific, actionable, and something my team would have spent three weeks and fifty thousand dirhams getting from a consultancy."

**For the respondent.** "I got a WhatsApp message, had an interesting 10-minute conversation about my neighborhood, and earned 40 dirhams. I didn't have to download anything or fill out any forms. It felt like someone actually wanted to hear what I had to say."

**For the system.** "We conducted 200 conversations across 15 demographic segments in 6 hours, produced an intelligence brief that identified three findings the business hadn't anticipated, and enriched our derived profiles for 200 respondents."

---

## Part 16: What This Is Not

**This is not a survey platform.** Surveys compress human experience into predefined boxes. MeshAI extracts insight through conversation. The Research Designer produces information objectives, not questionnaires. The Field Agent has a checklist, not a script.

**This is not a chatbot.** The Field Agent is an adaptive interviewer that uses professional qualitative research techniques — probing, laddering, narrative elicitation, rapport building. The difference: a chatbot responds. An interviewer listens.

**This is not a data dashboard.** The Analyst produces a synthesized intelligence brief with findings, confidence levels, tensions, and recommendations. Not bar charts. Not word clouds. The kind of deliverable a senior consultant would produce.

The relationship between the quality of human insight and the cost to obtain it has always been linear. MeshAI breaks that relationship. That's the product.