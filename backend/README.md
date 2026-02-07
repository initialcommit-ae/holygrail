# Backend (FastAPI + Twilio WhatsApp survey)

This backend runs a simple WhatsApp “survey bot”:

- `POST /start` accepts a list of questions and sends the first question via Twilio WhatsApp.
- Twilio calls `POST /twilio/inbound` for each incoming reply; the backend stores answers in a JSON file and sends the next question.
- Optionally, an AI agent rewrites each question to sound more conversational before sending.

## Setup

### 1) Create a venv and install deps

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Configure env vars

This project will auto-load `backend/.env` if present (recommended). You can also export these via your shell.

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_FROM` (**must** be a Twilio WhatsApp-enabled sender)
  - Twilio WhatsApp Sandbox: `whatsapp:+14155238886`
  - Or your approved Twilio WhatsApp sender (not your personal phone number)

Optional:

- `SURVEY_STATE_PATH` (default `survey_state.json`)
- `GEMINI_API_KEY` (enables AI question rewriting using `gemini-2.5-flash`)

### 3) Hardcode the WhatsApp recipient number

Edit `backend/app/config.py`:

- `WHATSAPP_TO = "whatsapp:+<your_number>"`

## Run

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

If you `cd backend/app`, you can also run:

```bash
uvicorn main:app --reload
```

## Twilio webhook

In Twilio Console for your WhatsApp sender, set:

- **WHEN A MESSAGE COMES IN** → `POST https://<your-public-domain>/twilio/inbound`

### Local dev with ngrok

```bash
ngrok http 8000
```

Then set Twilio webhook to:

- `https://<your-ngrok-domain>/twilio/inbound`

## Common “message not received” causes

- `TWILIO_WHATSAPP_FROM` is wrong (it must be the Twilio sandbox number or an approved Twilio WhatsApp sender)
- If using the sandbox: your WhatsApp number must first send the “join <code>” message to the sandbox to opt-in
- Twilio Console → Monitor → Logs → Messaging shows an error for the attempted send

## Endpoints

- `POST /start`
  - Body: `{ "questions": ["Question 1", "Question 2"] }`
- `POST /twilio/inbound`
  - Twilio form fields: `From`, `Body`, `MessageSid`
- `GET /state`
  - Returns the current JSON state (or `{ "status": "none" }`)
- `GET /analyze`
  - Generates `{ tsx, data }` for a sandboxed React analytics report (requires `GEMINI_API_KEY`)

## Smoke test checklist

1) Start server (see “Run”).

2) In another terminal:

```bash
curl -sS -X POST http://127.0.0.1:8000/start \
  -H 'content-type: application/json' \
  -d '{"questions":["Q1?","Q2?"]}' | python -m json.tool
```

3) Check state:

```bash
curl -sS http://127.0.0.1:8000/state | python -m json.tool
```

4) With Twilio webhook configured, reply on WhatsApp and confirm:

- answers append into `survey_state.json`
- next question gets sent
- completion message is sent after last question

