import sys
import time
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse

# Allow running either as a package (recommended):
#   uvicorn app.main:app --reload
# or from inside backend/app as:
#   uvicorn main:app --reload
#
# The latter imports this file as a top-level module, so we ensure the backend/
# directory is on sys.path and then use absolute imports via the `app` package.
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.config import WHATSAPP_TO  # noqa: E402
from app.models import StartRequest  # noqa: E402
from app.storage import load_state, new_state, save_state, touch_updated_at  # noqa: E402
from app.twilio_client import send_whatsapp  # noqa: E402


app = FastAPI()


@app.post("/start")
async def start(req: StartRequest, background: BackgroundTasks) -> dict[str, Any]:
    questions = [q.strip() for q in req.questions if isinstance(q, str)]
    questions = [q for q in questions if q]
    if not questions:
        raise HTTPException(status_code=400, detail="questions must be a non-empty list of strings")

    state = new_state(questions)
    save_state(state)

    def kickoff() -> None:
        send_whatsapp(WHATSAPP_TO, questions[0])

    background.add_task(kickoff)
    return {"ok": True, "sent_to": WHATSAPP_TO, "question_count": len(questions)}


@app.post("/twilio/inbound")
async def inbound(request: Request, background: BackgroundTasks) -> PlainTextResponse:
    """
    Twilio sends application/x-www-form-urlencoded.
    Fields include: From, Body, MessageSid.
    """

    form = await request.form()
    from_user = form.get("From")  # e.g. "whatsapp:+..."
    body = (form.get("Body") or "").strip()
    message_sid = form.get("MessageSid")

    # Ignore messages not from the hardcoded user.
    if from_user != WHATSAPP_TO:
        return PlainTextResponse("ignored", status_code=200)

    state = load_state()
    if not state or state.get("status") != "active":

        def no_active() -> None:
            send_whatsapp(WHATSAPP_TO, "No active survey right now.")

        background.add_task(no_active)
        return PlainTextResponse("ok", status_code=200)

    # Idempotency: Twilio may resend webhooks.
    if message_sid:
        processed = state.get("processed_message_sids") or []
        if message_sid in processed:
            return PlainTextResponse("ok", status_code=200)
        processed.append(message_sid)
        state["processed_message_sids"] = processed

    # Stop keywords
    if body.lower() in {"stop", "quit", "cancel", "end"}:
        state["status"] = "ended"
        touch_updated_at(state)
        save_state(state)

        def end_msg() -> None:
            send_whatsapp(WHATSAPP_TO, "Understood. Ending the survey now. Thank you for your time.")

        background.add_task(end_msg)
        return PlainTextResponse("ok", status_code=200)

    idx = state.get("index", 0)
    questions = state.get("questions") or []

    # Save answer for current question (idx points to the question last asked).
    if isinstance(idx, int) and 0 <= idx < len(questions):
        answers = state.get("answers")
        if not isinstance(answers, list):
            answers = []
            state["answers"] = answers
        answers.append({"q": questions[idx], "a": body, "ts": int(time.time())})
    else:
        state["status"] = "ended"
        touch_updated_at(state)
        save_state(state)
        return PlainTextResponse("ok", status_code=200)

    # Advance index and decide next step.
    state["index"] = idx + 1
    idx = state["index"]

    if idx >= len(questions):
        state["status"] = "completed"
        touch_updated_at(state)
        save_state(state)

        def done_msg() -> None:
            send_whatsapp(WHATSAPP_TO, "Thank you. The survey is complete.")

        background.add_task(done_msg)
        return PlainTextResponse("ok", status_code=200)

    touch_updated_at(state)
    save_state(state)

    next_q = questions[idx]

    def ask_next() -> None:
        send_whatsapp(WHATSAPP_TO, next_q)

    background.add_task(ask_next)
    return PlainTextResponse("ok", status_code=200)


@app.get("/state")
def get_state() -> dict[str, Any]:
    return load_state() or {"status": "none"}

