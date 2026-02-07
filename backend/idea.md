Got you. Here’s a clean, minimal FastAPI backend that does exactly this:

* `POST /start` receives `{"questions": ["...", "..."]}`
* Phone number is **hardcoded in code** (the WhatsApp user)
* Sends Q1 via Twilio WhatsApp
* Twilio hits `POST /twilio/inbound` when the user replies
* Saves answers + progress into a **JSON file**
* Sends next question until finished

## Install

```bash
pip install fastapi uvicorn twilio python-multipart
```

## Set env vars

```bash
export TWILIO_ACCOUNT_SID="..."
export TWILIO_AUTH_TOKEN="..."
export TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"  # or your approved WhatsApp sender
```

## `main.py`

```python
import os
import json
import time
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse
from twilio.rest import Client

app = FastAPI()

# ----------------------------
# CONFIG (hardcoded user phone)
# ----------------------------
WHATSAPP_TO = "whatsapp:+971XXXXXXXXX"  # <-- hardcode the user's WhatsApp number here

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = os.environ["TWILIO_WHATSAPP_FROM"]  # e.g. "whatsapp:+14155238886"

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

DATA_PATH = "survey_state.json"


# ----------------------------
# Storage helpers (JSON file)
# ----------------------------
def load_state() -> Optional[Dict[str, Any]]:
    if not os.path.exists(DATA_PATH):
        return None
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: Dict[str, Any]) -> None:
    # atomic-ish write
    tmp = DATA_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)

def new_state(questions: List[str]) -> Dict[str, Any]:
    return {
        "created_at": int(time.time()),
        "status": "active",  # active | completed | ended
        "to": WHATSAPP_TO,
        "questions": questions,
        "index": 0,
        "answers": []  # list of {"q": "...", "a": "...", "ts": ...}
    }


# ----------------------------
# Twilio helper
# ----------------------------
def send_whatsapp(to_user: str, text: str) -> str:
    msg = twilio_client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        to=to_user,
        body=text
    )
    return msg.sid


# ----------------------------
# Endpoint: start survey
# ----------------------------
@app.post("/start")
async def start(payload: Dict[str, Any], background: BackgroundTasks):
    """
    Body:
    {
      "questions": ["Question 1", "Question 2", ...]
    }
    """
    questions = payload.get("questions")
    if not isinstance(questions, list) or not all(isinstance(q, str) and q.strip() for q in questions):
        raise HTTPException(status_code=400, detail="questions must be a non-empty list of strings")

    state = new_state([q.strip() for q in questions])
    save_state(state)

    # send first question asynchronously
    def kickoff():
        send_whatsapp(WHATSAPP_TO, state["questions"][0])

    background.add_task(kickoff)

    return {"ok": True, "sent_to": WHATSAPP_TO, "question_count": len(questions)}


# ----------------------------
# Twilio inbound webhook
# ----------------------------
@app.post("/twilio/inbound")
async def inbound(request: Request, background: BackgroundTasks):
    """
    Twilio sends application/x-www-form-urlencoded
    Fields include: From, Body, MessageSid
    """
    form = await request.form()
    from_user = form.get("From")  # "whatsapp:+..."
    body = (form.get("Body") or "").strip()

    # Ignore messages not from the hardcoded user
    if from_user != WHATSAPP_TO:
        return PlainTextResponse("ignored", status_code=200)

    state = load_state()
    if not state or state.get("status") != "active":
        # No active survey. Optionally message user.
        def no_active():
            send_whatsapp(WHATSAPP_TO, "No active survey right now.")
        background.add_task(no_active)
        return PlainTextResponse("ok", status_code=200)

    # Stop keywords
    if body.lower() in {"stop", "quit", "cancel", "end"}:
        state["status"] = "ended"
        save_state(state)

        def end_msg():
            send_whatsapp(WHATSAPP_TO, "Understood. Ending the survey now. Thank you for your time.")
        background.add_task(end_msg)
        return PlainTextResponse("ok", status_code=200)

    idx = state["index"]
    questions = state["questions"]

    # Save answer for current question (idx should point to the question last asked)
    if 0 <= idx < len(questions):
        state["answers"].append({"q": questions[idx], "a": body, "ts": int(time.time())})
    else:
        # If index is out of bounds, mark ended to avoid looping
        state["status"] = "ended"
        save_state(state)
        return PlainTextResponse("ok", status_code=200)

    # Advance index and decide next step
    state["index"] += 1
    idx = state["index"]

    if idx >= len(questions):
        state["status"] = "completed"
        save_state(state)

        def done_msg():
            send_whatsapp(WHATSAPP_TO, "Thank you. The survey is complete.")
        background.add_task(done_msg)
        return PlainTextResponse("ok", status_code=200)

    # Persist state before sending next question
    save_state(state)

    next_q = questions[idx]

    def ask_next():
        send_whatsapp(WHATSAPP_TO, next_q)

    background.add_task(ask_next)
    return PlainTextResponse("ok", status_code=200)


# ----------------------------
# Convenience endpoint: check state
# ----------------------------
@app.get("/state")
def get_state():
    return load_state() or {"status": "none"}
```

## Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Twilio webhook URL

In Twilio Console for your WhatsApp sender:

* **WHEN A MESSAGE COMES IN** → `POST https://<your-public-domain>/twilio/inbound`

If local dev, expose with ngrok:

```bash
ngrok http 8000
```

Then use `https://xxxx.ngrok-free.app/twilio/inbound`

---

## Notes (important)

* This supports **one active survey at a time** (single JSON file). If you want many users later, switch to Redis/Postgres and key by `From`.
* Twilio may resend webhooks sometimes; for production, add idempotency using `MessageSid` to avoid duplicate saves.

If you want, I can modify this to support **multiple concurrent WhatsApp users** while still saving each session as its own JSON file (one per phone / session_id).




74F5RXEMXHY7V39M5PZ3H9MG