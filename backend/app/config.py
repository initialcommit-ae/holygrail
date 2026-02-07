import os
from pathlib import Path

from dotenv import load_dotenv


# ----------------------------
# CONFIG (hardcoded user phone)
# ----------------------------
# Twilio sends WhatsApp From numbers as "whatsapp:+<E164>".
WHATSAPP_TO = "whatsapp:+971543856026"  # TODO: replace with your WhatsApp number


_BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_BACKEND_DIR / ".env")

# Gemini / Google API key mapping for PydanticAI (expects GOOGLE_API_KEY for google-gla)
_gemini_api_key = os.environ.get("GEMINI_API_KEY")
if _gemini_api_key and not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = _gemini_api_key


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


TWILIO_ACCOUNT_SID = _require_env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = _require_env("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = _require_env("TWILIO_WHATSAPP_FROM")

# Storage
DATA_PATH = os.environ.get("SURVEY_STATE_PATH", "survey_state.json")

