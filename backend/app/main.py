import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from app.config import MAX_CONCURRENT_LLM_CALLS  # noqa: E402
from app.conversation_agent import get_agent_response  # noqa: E402
from app.db import close_pool, create_pool, get_pool  # noqa: E402
from app.models import CreateCampaignRequest  # noqa: E402
from app.outreach_worker import start_outreach_worker, stop_outreach_worker  # noqa: E402
from app.twilio_client import send_whatsapp  # noqa: E402

logger = logging.getLogger("backend")
logging.basicConfig(level=logging.INFO)

_llm_semaphore: asyncio.Semaphore | None = None

STOP_KEYWORDS = {"stop", "quit", "cancel", "end"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _llm_semaphore
    _llm_semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)
    await create_pool()
    start_outreach_worker()
    yield
    stop_outreach_worker()
    await close_pool()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Campaign endpoints
# ---------------------------------------------------------------------------


@app.post("/campaigns")
async def create_campaign(req: CreateCampaignRequest) -> dict[str, Any]:
    pool = get_pool()
    extraction_schema = {
        k: {"type": v.type, "description": v.description}
        for k, v in req.extraction_schema.items()
    }

    row = await pool.fetchrow(
        """
        INSERT INTO campaigns (name, research_brief, extraction_schema,
                               system_prompt_override, phone_numbers, status)
        VALUES ($1, $2, $3, $4, $5, 'draft')
        RETURNING id, created_at
        """,
        req.name,
        req.research_brief,
        json.dumps(extraction_schema),
        req.system_prompt_override,
        req.phone_numbers,
    )

    return {
        "ok": True,
        "campaign_id": str(row["id"]),
        "created_at": row["created_at"].isoformat(),
    }


@app.get("/campaigns")
async def list_campaigns() -> list[dict[str, Any]]:
    pool = get_pool()
    rows = await pool.fetch(
        """
        SELECT id, name, status, total_conversations, completed_conversations, created_at
        FROM campaigns ORDER BY created_at DESC
        """
    )
    return [
        {
            "id": str(r["id"]),
            "name": r["name"],
            "status": r["status"],
            "total_conversations": r["total_conversations"],
            "completed_conversations": r["completed_conversations"],
            "created_at": r["created_at"].isoformat(),
        }
        for r in rows
    ]


@app.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: UUID) -> dict[str, Any]:
    pool = get_pool()
    row = await pool.fetchrow("SELECT * FROM campaigns WHERE id = $1", campaign_id)
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "research_brief": row["research_brief"],
        "extraction_schema": json.loads(row["extraction_schema"])
        if isinstance(row["extraction_schema"], str)
        else row["extraction_schema"],
        "phone_numbers": row["phone_numbers"],
        "status": row["status"],
        "total_conversations": row["total_conversations"],
        "completed_conversations": row["completed_conversations"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
    }


@app.post("/campaigns/{campaign_id}/launch")
async def launch_campaign(campaign_id: UUID) -> dict[str, Any]:
    pool = get_pool()
    campaign = await pool.fetchrow("SELECT * FROM campaigns WHERE id = $1", campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign["status"] not in ("draft", "paused"):
        raise HTTPException(status_code=400, detail=f"Cannot launch campaign with status '{campaign['status']}'")

    phone_numbers = campaign["phone_numbers"]
    now = datetime.now(timezone.utc)
    rate = 10  # messages per minute
    conversations_created = 0

    async with pool.acquire() as conn:
        async with conn.transaction():
            for i, phone in enumerate(phone_numbers):
                # Stagger: 10 per minute -> each batch of 10 gets a 1-minute delay
                delay_seconds = (i // rate) * 60 + (i % rate) * 6
                scheduled_at = now + timedelta(seconds=delay_seconds)

                # Upsert user
                user_row = await conn.fetchrow(
                    """
                    INSERT INTO users (phone_number)
                    VALUES ($1)
                    ON CONFLICT (phone_number) DO UPDATE SET phone_number = EXCLUDED.phone_number
                    RETURNING id
                    """,
                    phone,
                )

                # Create conversation
                conv_row = await conn.fetchrow(
                    """
                    INSERT INTO conversations (campaign_id, user_id, phone_number, status)
                    VALUES ($1, $2, $3, 'pending')
                    ON CONFLICT (campaign_id, phone_number) DO NOTHING
                    RETURNING id
                    """,
                    campaign_id,
                    user_row["id"],
                    phone,
                )
                if not conv_row:
                    continue  # Already exists

                # Schedule outreach
                await conn.execute(
                    """
                    INSERT INTO outreach_queue (conversation_id, scheduled_at, status)
                    VALUES ($1, $2, 'pending')
                    """,
                    conv_row["id"],
                    scheduled_at,
                )
                conversations_created += 1

            # Activate campaign
            await conn.execute(
                """
                UPDATE campaigns
                SET status = 'active',
                    total_conversations = total_conversations + $2,
                    updated_at = NOW()
                WHERE id = $1
                """,
                campaign_id,
                conversations_created,
            )

    estimated_minutes = max(1, (conversations_created // rate) + 1)

    return {
        "ok": True,
        "conversations_created": conversations_created,
        "estimated_completion_minutes": estimated_minutes,
        "outreach_rate_per_minute": rate,
    }


@app.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(campaign_id: UUID) -> dict[str, Any]:
    pool = get_pool()
    campaign = await pool.fetchrow("SELECT status FROM campaigns WHERE id = $1", campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign["status"] != "active":
        raise HTTPException(status_code=400, detail="Can only pause active campaigns")

    await pool.execute(
        "UPDATE campaigns SET status = 'paused', updated_at = NOW() WHERE id = $1",
        campaign_id,
    )
    # Cancel pending outreach
    await pool.execute(
        """
        UPDATE outreach_queue SET status = 'failed', error = 'campaign paused'
        WHERE conversation_id IN (SELECT id FROM conversations WHERE campaign_id = $1)
          AND status = 'pending'
        """,
        campaign_id,
    )
    return {"ok": True}


@app.get("/campaigns/{campaign_id}/conversations")
async def list_conversations(campaign_id: UUID) -> list[dict[str, Any]]:
    pool = get_pool()
    rows = await pool.fetch(
        """
        SELECT id, phone_number, status, extracted_data, message_count,
               created_at, updated_at, completed_at
        FROM conversations
        WHERE campaign_id = $1
        ORDER BY created_at
        """,
        campaign_id,
    )
    return [
        {
            "id": str(r["id"]),
            "phone_number": r["phone_number"],
            "status": r["status"],
            "extracted_data": json.loads(r["extracted_data"])
            if isinstance(r["extracted_data"], str)
            else r["extracted_data"],
            "message_count": r["message_count"],
            "created_at": r["created_at"].isoformat(),
            "updated_at": r["updated_at"].isoformat(),
            "completed_at": r["completed_at"].isoformat() if r["completed_at"] else None,
        }
        for r in rows
    ]


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: UUID) -> dict[str, Any]:
    pool = get_pool()
    conv = await pool.fetchrow(
        "SELECT * FROM conversations WHERE id = $1", conversation_id
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msgs = await pool.fetch(
        """
        SELECT sender, content, twilio_sid, created_at
        FROM messages WHERE conversation_id = $1
        ORDER BY created_at
        """,
        conversation_id,
    )

    return {
        "id": str(conv["id"]),
        "campaign_id": str(conv["campaign_id"]),
        "phone_number": conv["phone_number"],
        "status": conv["status"],
        "extracted_data": json.loads(conv["extracted_data"])
        if isinstance(conv["extracted_data"], str)
        else conv["extracted_data"],
        "message_count": conv["message_count"],
        "messages": [
            {
                "sender": m["sender"],
                "content": m["content"],
                "twilio_sid": m["twilio_sid"],
                "created_at": m["created_at"].isoformat(),
            }
            for m in msgs
        ],
    }


@app.get("/campaigns/{campaign_id}/extractions")
async def get_extractions(campaign_id: UUID) -> dict[str, Any]:
    pool = get_pool()
    campaign = await pool.fetchrow("SELECT * FROM campaigns WHERE id = $1", campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    rows = await pool.fetch(
        """
        SELECT phone_number, status, extracted_data
        FROM conversations
        WHERE campaign_id = $1 AND status = 'completed'
        ORDER BY completed_at
        """,
        campaign_id,
    )

    extractions = []
    for r in rows:
        data = (
            json.loads(r["extracted_data"])
            if isinstance(r["extracted_data"], str)
            else r["extracted_data"]
        )
        extractions.append({
            "phone_number": r["phone_number"],
            "data": data,
        })

    return {
        "campaign_id": str(campaign_id),
        "total_completed": len(extractions),
        "extractions": extractions,
    }


# ---------------------------------------------------------------------------
# Twilio inbound webhook
# ---------------------------------------------------------------------------


@app.post("/twilio/inbound")
async def inbound(request: Request, background: BackgroundTasks) -> PlainTextResponse:
    form = await request.form()
    from_user = str(form.get("From") or "")
    body = str(form.get("Body") or "").strip()
    twilio_sid = str(form.get("MessageSid") or "")

    # Normalize: "whatsapp:+971..." -> "+971..."
    phone = from_user.replace("whatsapp:", "")
    if not phone:
        return PlainTextResponse("", status_code=200)

    # Persist message and process async — return 200 to Twilio fast
    background.add_task(_process_inbound, phone, body, twilio_sid)
    return PlainTextResponse("", status_code=200)


async def _process_inbound(phone: str, body: str, twilio_sid: str) -> None:
    pool = get_pool()

    # Idempotency check
    if twilio_sid:
        existing = await pool.fetchval(
            "SELECT id FROM messages WHERE twilio_sid = $1", twilio_sid
        )
        if existing:
            logger.info("Duplicate webhook for twilio_sid=%s, skipping", twilio_sid)
            return

    # Find active conversation for this phone number
    conv = await pool.fetchrow(
        """
        SELECT c.*, cam.research_brief, cam.extraction_schema,
               cam.system_prompt_override, cam.status AS campaign_status
        FROM conversations c
        JOIN campaigns cam ON c.campaign_id = cam.id
        WHERE c.phone_number = $1
          AND c.status IN ('outreach_sent', 'active')
          AND cam.status = 'active'
        ORDER BY c.created_at DESC
        LIMIT 1
        """,
        phone,
    )
    if not conv:
        logger.info("No active conversation for phone=%s", phone)
        return

    conv_id = conv["id"]

    # Advisory lock on conversation to prevent race conditions
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "SELECT pg_advisory_xact_lock(hashtext($1::text))",
                str(conv_id),
            )

            # Save inbound message
            await conn.execute(
                """
                INSERT INTO messages (conversation_id, sender, content, twilio_sid)
                VALUES ($1, 'user', $2, $3)
                """,
                conv_id,
                body,
                twilio_sid or None,
            )

            # Update conversation status if it was outreach_sent
            if conv["status"] == "outreach_sent":
                await conn.execute(
                    "UPDATE conversations SET status = 'active', updated_at = NOW() WHERE id = $1",
                    conv_id,
                )

            # Check stop keywords
            if body.lower().strip() in STOP_KEYWORDS:
                await conn.execute(
                    """
                    UPDATE conversations
                    SET status = 'abandoned', updated_at = NOW(), completed_at = NOW()
                    WHERE id = $1
                    """,
                    conv_id,
                )
                _safe_send(phone, "Understood — thanks for your time! Take care.")
                return

            # Load full message history
            msg_rows = await conn.fetch(
                """
                SELECT sender, content FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at
                """,
                conv_id,
            )
            conversation_history = [
                {"sender": m["sender"], "content": m["content"]}
                for m in msg_rows
            ]

            # Get extraction state
            extracted_data = conv["extracted_data"]
            if isinstance(extracted_data, str):
                extracted_data = json.loads(extracted_data)
            extracted_data = extracted_data or {}

            extraction_schema = conv["extraction_schema"]
            if isinstance(extraction_schema, str):
                extraction_schema = json.loads(extraction_schema)

    # Call LLM (outside transaction — this is slow)
    assert _llm_semaphore is not None
    async with _llm_semaphore:
        try:
            agent_resp = await get_agent_response(
                research_brief=conv["research_brief"],
                extraction_schema=extraction_schema,
                extracted_data=extracted_data,
                conversation_history=conversation_history,
                system_prompt_override=conv["system_prompt_override"],
            )
        except Exception:
            logger.exception("Agent failed for conversation=%s", conv_id)
            return

    # Merge extracted data
    merged_data = {**extracted_data, **agent_resp.extracted_data_update}

    # Persist agent response and update conversation
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "SELECT pg_advisory_xact_lock(hashtext($1::text))",
                str(conv_id),
            )

            await conn.execute(
                """
                INSERT INTO messages (conversation_id, sender, content)
                VALUES ($1, 'agent', $2)
                """,
                conv_id,
                agent_resp.message,
            )

            if agent_resp.conversation_complete:
                await conn.execute(
                    """
                    UPDATE conversations
                    SET extracted_data = $2, message_count = message_count + 2,
                        status = 'completed', completed_at = NOW(), updated_at = NOW()
                    WHERE id = $1
                    """,
                    conv_id,
                    json.dumps(merged_data),
                )
                await conn.execute(
                    """
                    UPDATE campaigns
                    SET completed_conversations = completed_conversations + 1,
                        updated_at = NOW()
                    WHERE id = $1
                    """,
                    conv["campaign_id"],
                )
            else:
                await conn.execute(
                    """
                    UPDATE conversations
                    SET extracted_data = $2, message_count = message_count + 2,
                        updated_at = NOW()
                    WHERE id = $1
                    """,
                    conv_id,
                    json.dumps(merged_data),
                )

    # Send response via Twilio
    _safe_send(phone, agent_resp.message)

    # Check if all conversations are completed
    if agent_resp.conversation_complete:
        await _check_campaign_completion(conv["campaign_id"])


async def _check_campaign_completion(campaign_id: UUID) -> None:
    pool = get_pool()
    row = await pool.fetchrow(
        "SELECT total_conversations, completed_conversations FROM campaigns WHERE id = $1",
        campaign_id,
    )
    if row and row["completed_conversations"] >= row["total_conversations"] > 0:
        await pool.execute(
            "UPDATE campaigns SET status = 'completed', updated_at = NOW() WHERE id = $1",
            campaign_id,
        )
        logger.info("Campaign %s completed", campaign_id)


def _safe_send(phone: str, text: str) -> None:
    try:
        to = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
        sid = send_whatsapp(to, text)
        logger.info("Sent WhatsApp message sid=%s to=%s", sid, phone)
    except Exception:
        logger.exception("Failed to send WhatsApp message to %s", phone)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
