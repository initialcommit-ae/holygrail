import json
import os
import time
from typing import Any, Dict, List, Optional

from .config import DATA_PATH, WHATSAPP_TO


State = Dict[str, Any]


def load_state() -> Optional[State]:
    if not os.path.exists(DATA_PATH):
        return None
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: State) -> None:
    # atomic-ish write
    tmp = f"{DATA_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_PATH)


def new_state(questions: List[str]) -> State:
    now = int(time.time())
    return {
        "created_at": now,
        "updated_at": now,
        "status": "active",  # active | completed | ended
        "to": WHATSAPP_TO,
        "questions": questions,
        "index": 0,
        "answers": [],  # list of {"q": "...", "a": "...", "ts": ...}
        "processed_message_sids": [],  # Twilio MessageSid idempotency
    }


def touch_updated_at(state: State) -> None:
    state["updated_at"] = int(time.time())

