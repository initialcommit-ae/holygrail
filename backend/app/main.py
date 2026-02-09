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

from app.config import MAX_CONCURRENT_LLM_CALLS, OUTREACH_RATE_PER_MINUTE  # noqa: E402
from app.conversation_agent import MeshContext, get_agent_response  # noqa: E402
from app.db import close_pool, create_pool, get_pool  # noqa: E402
from app.models import CreateCampaignRequest  # noqa: E402
from app.outreach_worker import start_outreach_worker, stop_outreach_worker  # noqa: E402
from app.twilio_client import send_whatsapp  # noqa: E402

logger = logging.getLogger("backend")
logging.basicConfig(level=logging.INFO)

_llm_semaphore: asyncio.Semaphore | None = None

STOP_KEYWORDS = {"stop", "quit", "cancel", "end"}

# Demographics required for "onboarded" status
_REQUIRED_DEMOGRAPHICS = ("city", "age_range", "gender")


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
                               system_prompt_override, phone_numbers,
                               reward_text, reward_link, targeting, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'draft')
        RETURNING id, created_at
        """,
        req.name,
        req.research_brief,
        json.dumps(extraction_schema),
        req.system_prompt_override,
        req.phone_numbers,
        req.reward_text,
        req.reward_link,
        json.dumps(req.targeting) if req.targeting else None,
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

    targeting = row["targeting"]
    if isinstance(targeting, str):
        targeting = json.loads(targeting)

    return {
        "id": str(row["id"]),
        "name": row["name"],
        "research_brief": row["research_brief"],
        "extraction_schema": json.loads(row["extraction_schema"])
        if isinstance(row["extraction_schema"], str)
        else row["extraction_schema"],
        "phone_numbers": row["phone_numbers"],
        "reward_text": row["reward_text"],
        "reward_link": row["reward_link"],
        "targeting": targeting,
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

    phone_numbers = campaign["phone_numbers"] or []
    now = datetime.now(timezone.utc)
    rate = max(1, OUTREACH_RATE_PER_MINUTE)
    conversations_created = 0
    reactivated_outreach = 0

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Re-activate paused outreach in staggered order to avoid burst sends.
            if campaign["status"] == "paused":
                paused_rows = await conn.fetch(
                    """
                    SELECT oq.id
                    FROM outreach_queue oq
                    JOIN conversations c ON c.id = oq.conversation_id
                    WHERE c.campaign_id = $1
                      AND oq.status = 'paused'
                    ORDER BY oq.scheduled_at, oq.id
                    """,
                    campaign_id,
                )
                for i, row in enumerate(paused_rows):
                    delay_seconds = int((i * 60) / rate)
                    await conn.execute(
                        """
                        UPDATE outreach_queue
                        SET status = 'pending', scheduled_at = $2, error = NULL
                        WHERE id = $1
                        """,
                        row["id"],
                        now + timedelta(seconds=delay_seconds),
                    )
                reactivated_outreach = len(paused_rows)

            for i, phone in enumerate(phone_numbers):
                delay_seconds = int(((reactivated_outreach + i) * 60) / rate)
                scheduled_at = now + timedelta(seconds=delay_seconds)

                # Upsert user — preserve existing status, default 'new' for new users
                user_row = await conn.fetchrow(
                    """
                    INSERT INTO users (phone_number, status)
                    VALUES ($1, 'new')
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
                    ON CONFLICT (campaign_id, phone_number)
                        WHERE campaign_id IS NOT NULL
                        DO NOTHING
                    RETURNING id
                    """,
                    campaign_id,
                    user_row["id"],
                    phone,
                )
                if not conv_row:
                    continue

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

    total_scheduled = reactivated_outreach + conversations_created
    estimated_minutes = max(1, (total_scheduled // rate) + 1)

    return {
        "ok": True,
        "conversations_created": conversations_created,
        "reactivated_outreach": reactivated_outreach,
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
    await pool.execute(
        """
        UPDATE outreach_queue SET status = 'paused'
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
        "campaign_id": str(conv["campaign_id"]) if conv["campaign_id"] else None,
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

    phone = from_user.replace("whatsapp:", "")
    if not phone:
        return PlainTextResponse("", status_code=200)

    background.add_task(_process_inbound, phone, body, twilio_sid)
    return PlainTextResponse("", status_code=200)


# ---------------------------------------------------------------------------
# Inbound routing — the full decision tree
# ---------------------------------------------------------------------------


async def _process_inbound(phone: str, body: str, twilio_sid: str) -> None:
    pool = get_pool()

    # Idempotency: advisory lock on twilio_sid hash serializes duplicate webhooks,
    # then check + unique index (uq_messages_twilio_sid) enforces exactly-once.
    if twilio_sid:
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "SELECT pg_advisory_xact_lock(hashtext($1))", twilio_sid
                )
                existing = await conn.fetchval(
                    "SELECT id FROM messages WHERE twilio_sid = $1", twilio_sid
                )
                if existing:
                    logger.info("Duplicate webhook for twilio_sid=%s, skipping", twilio_sid)
                    return

    # Step 1: Lookup user by phone
    user = await pool.fetchrow(
        "SELECT * FROM users WHERE phone_number = $1", phone
    )

    if not user:
        # New user — create + start onboarding
        user = await pool.fetchrow(
            """
            INSERT INTO users (phone_number, status)
            VALUES ($1, 'new')
            ON CONFLICT (phone_number) DO UPDATE SET phone_number = EXCLUDED.phone_number
            RETURNING *
            """,
            phone,
        )
        conv = await _get_or_create_active_onboarding_conversation(user["id"], phone)
        await _handle_onboarding(conv, user, phone, body, twilio_sid)
        return

    # Step 2: Find active conversation
    conv = await pool.fetchrow(
        """
        SELECT c.*, cam.research_brief, cam.extraction_schema,
               cam.system_prompt_override, cam.reward_text, cam.reward_link
        FROM conversations c
        LEFT JOIN campaigns cam ON c.campaign_id = cam.id
        WHERE c.user_id = $1
          AND c.status IN ('active', 'bounty_sent')
        ORDER BY c.created_at DESC
        LIMIT 1
        """,
        user["id"],
    )

    if not conv:
        # If onboarding is incomplete and no active thread exists, resume onboarding.
        if user["status"] in ("new", "onboarding"):
            conv = await _get_or_create_active_onboarding_conversation(user["id"], phone)
            await _handle_onboarding(conv, user, phone, body, twilio_sid)
        else:
            # User is idle — general mode
            await _handle_general(user, phone, body, twilio_sid)
        return

    # Step 3: Route by conversation state
    if conv["status"] == "bounty_sent" and conv["campaign_id"] is not None:
        await _handle_bounty_response(conv, user, phone, body, twilio_sid)
    elif conv["status"] == "active" and conv["campaign_id"] is not None:
        await _handle_campaign(conv, user, phone, body, twilio_sid)
    elif conv["status"] == "active" and conv["campaign_id"] is None:
        await _handle_onboarding(conv, user, phone, body, twilio_sid)
    else:
        logger.warning("Unexpected conv state: status=%s campaign_id=%s", conv["status"], conv["campaign_id"])
        await _handle_general(user, phone, body, twilio_sid)


# ---------------------------------------------------------------------------
# Handler: Onboarding
# ---------------------------------------------------------------------------


async def _handle_onboarding(conv, user, phone: str, body: str, twilio_sid: str) -> None:
    pool = get_pool()
    conv_id = conv["id"]

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock(hashtext($1::text))", str(conv_id))

            # Save inbound message (dedupe-safe on twilio_sid)
            inserted = await _insert_inbound_user_message(conn, conv_id, body, twilio_sid)
            if not inserted:
                logger.info("Duplicate inbound message ignored for conversation=%s", conv_id)
                return

            # Update user status to onboarding if new
            if user["status"] == "new":
                await conn.execute(
                    "UPDATE users SET status = 'onboarding' WHERE id = $1", user["id"]
                )

            # Check stop keywords
            if body.lower().strip() in STOP_KEYWORDS:
                await conn.execute(
                    "UPDATE conversations SET status = 'abandoned', updated_at = NOW(), completed_at = NOW() WHERE id = $1",
                    conv_id,
                )
                _safe_send(phone, "Understood — thanks for your time! Take care.")
                return

            # Load conversation history
            conversation_history = await _load_history(conn, conv_id)

    # Build context + call LLM
    deps = MeshContext(
        mode="onboarding",
        conversation_history=conversation_history,
        user_demographics=_user_demographics(user),
    )

    agent_resp = await _call_llm(deps, conv_id)
    if not agent_resp:
        return

    # Persist response + update demographics
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock(hashtext($1::text))", str(conv_id))

            await conn.execute(
                "INSERT INTO messages (conversation_id, sender, content) VALUES ($1, 'agent', $2)",
                conv_id, agent_resp.message,
            )

            # Update demographics
            became_onboarded = await _update_user_demographics(
                conn, user["id"], agent_resp.user_demographics_update, user,
            )

            if agent_resp.conversation_complete:
                await conn.execute(
                    """
                    UPDATE conversations
                    SET status = 'completed', message_count = message_count + 2,
                        updated_at = NOW(), completed_at = NOW()
                    WHERE id = $1
                    """,
                    conv_id,
                )
                # _update_user_demographics already sets onboarded if demographics are filled.
                # Do NOT force onboarded here — trust actual demographics, not LLM signal.
            else:
                await conn.execute(
                    "UPDATE conversations SET message_count = message_count + 2, updated_at = NOW() WHERE id = $1",
                    conv_id,
                )

    _safe_send(phone, agent_resp.message)


# ---------------------------------------------------------------------------
# Handler: Bounty response (accept/decline)
# ---------------------------------------------------------------------------


async def _handle_bounty_response(conv, user, phone: str, body: str, twilio_sid: str) -> None:
    pool = get_pool()
    conv_id = conv["id"]
    stop_requested = False

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock(hashtext($1::text))", str(conv_id))

            inserted = await _insert_inbound_user_message(conn, conv_id, body, twilio_sid)
            if not inserted:
                logger.info("Duplicate inbound message ignored for conversation=%s", conv_id)
                return

            # Check stop keywords
            if body.lower().strip() in STOP_KEYWORDS:
                await conn.execute(
                    "UPDATE conversations SET status = 'abandoned', updated_at = NOW(), completed_at = NOW() WHERE id = $1",
                    conv_id,
                )
                stop_requested = True
            else:
                conversation_history = await _load_history(conn, conv_id)

    if stop_requested:
        _safe_send(phone, "Understood — thanks for your time! Take care.")
        if conv["campaign_id"]:
            await _check_campaign_completion(conv["campaign_id"])
        return

    extraction_schema = conv["extraction_schema"]
    if isinstance(extraction_schema, str):
        extraction_schema = json.loads(extraction_schema)

    deps = MeshContext(
        mode="bounty",
        conversation_history=conversation_history,
        user_demographics=_user_demographics(user),
        research_brief=conv["research_brief"],
        extraction_schema=extraction_schema,
        reward_text=conv["reward_text"],
        reward_link=conv["reward_link"],
    )

    agent_resp = await _call_llm(deps, conv_id)
    if not agent_resp:
        return

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock(hashtext($1::text))", str(conv_id))

            await conn.execute(
                "INSERT INTO messages (conversation_id, sender, content) VALUES ($1, 'agent', $2)",
                conv_id, agent_resp.message,
            )

            if agent_resp.bounty_accepted is True:
                # Accepted — transition to active campaign conversation
                await conn.execute(
                    "UPDATE conversations SET status = 'active', message_count = message_count + 2, updated_at = NOW() WHERE id = $1",
                    conv_id,
                )
            elif agent_resp.bounty_accepted is False:
                # Declined
                await conn.execute(
                    """
                    UPDATE conversations
                    SET status = 'declined', message_count = message_count + 2,
                        updated_at = NOW(), completed_at = NOW()
                    WHERE id = $1
                    """,
                    conv_id,
                )
            else:
                # Ambiguous — keep bounty_sent, just update message count
                await conn.execute(
                    "UPDATE conversations SET message_count = message_count + 2, updated_at = NOW() WHERE id = $1",
                    conv_id,
                )

            # Update demographics if any
            await _update_user_demographics(
                conn, user["id"], agent_resp.user_demographics_update, user,
            )

    _safe_send(phone, agent_resp.message)

    # Check campaign completion on terminal states
    if agent_resp.bounty_accepted is False and conv["campaign_id"]:
        await _check_campaign_completion(conv["campaign_id"])


# ---------------------------------------------------------------------------
# Handler: Campaign conversation
# ---------------------------------------------------------------------------


async def _handle_campaign(conv, user, phone: str, body: str, twilio_sid: str) -> None:
    pool = get_pool()
    conv_id = conv["id"]
    stop_requested = False

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock(hashtext($1::text))", str(conv_id))

            inserted = await _insert_inbound_user_message(conn, conv_id, body, twilio_sid)
            if not inserted:
                logger.info("Duplicate inbound message ignored for conversation=%s", conv_id)
                return

            # Check stop keywords
            if body.lower().strip() in STOP_KEYWORDS:
                await conn.execute(
                    "UPDATE conversations SET status = 'abandoned', updated_at = NOW(), completed_at = NOW() WHERE id = $1",
                    conv_id,
                )
                stop_requested = True
            else:
                conversation_history = await _load_history(conn, conv_id)

    if stop_requested:
        _safe_send(phone, "Understood — thanks for your time! Take care.")
        if conv["campaign_id"]:
            await _check_campaign_completion(conv["campaign_id"])
        return

    extracted_data = conv["extracted_data"]
    if isinstance(extracted_data, str):
        extracted_data = json.loads(extracted_data)
    extracted_data = extracted_data or {}

    extraction_schema = conv["extraction_schema"]
    if isinstance(extraction_schema, str):
        extraction_schema = json.loads(extraction_schema)

    deps = MeshContext(
        mode="campaign",
        conversation_history=conversation_history,
        user_demographics=_user_demographics(user),
        research_brief=conv["research_brief"],
        extraction_schema=extraction_schema,
        extracted_data=extracted_data,
        reward_text=conv["reward_text"],
        reward_link=conv["reward_link"],
        system_prompt_override=conv["system_prompt_override"],
    )

    agent_resp = await _call_llm(deps, conv_id)
    if not agent_resp:
        return

    merged_data = {**extracted_data, **agent_resp.extracted_data_update}

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute("SELECT pg_advisory_xact_lock(hashtext($1::text))", str(conv_id))

            await conn.execute(
                "INSERT INTO messages (conversation_id, sender, content) VALUES ($1, 'agent', $2)",
                conv_id, agent_resp.message,
            )

            # Update demographics if any
            await _update_user_demographics(
                conn, user["id"], agent_resp.user_demographics_update, user,
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

    _safe_send(phone, agent_resp.message)

    if agent_resp.conversation_complete:
        await _check_campaign_completion(conv["campaign_id"])


# ---------------------------------------------------------------------------
# Handler: General (idle user)
# ---------------------------------------------------------------------------


async def _handle_general(user, phone: str, body: str, twilio_sid: str) -> None:
    pool = get_pool()

    # Create ephemeral conversation for message storage
    conv = await pool.fetchrow(
        """
        INSERT INTO conversations (user_id, phone_number, status)
        VALUES ($1, $2, 'active')
        RETURNING *
        """,
        user["id"],
        phone,
    )
    conv_id = conv["id"]

    async with pool.acquire() as conn:
        async with conn.transaction():
            inserted = await _insert_inbound_user_message(conn, conv_id, body, twilio_sid)
            if not inserted:
                logger.info("Duplicate inbound message ignored for conversation=%s", conv_id)
                await conn.execute(
                    """
                    UPDATE conversations
                    SET status = 'abandoned', updated_at = NOW(), completed_at = NOW()
                    WHERE id = $1
                    """,
                    conv_id,
                )
                return

            # Check stop keywords — in general mode, just acknowledge
            if body.lower().strip() in STOP_KEYWORDS:
                await conn.execute(
                    "UPDATE conversations SET status = 'abandoned', updated_at = NOW(), completed_at = NOW() WHERE id = $1",
                    conv_id,
                )
                _safe_send(phone, "Understood — thanks for your time! Take care.")
                return

            conversation_history = await _load_history(conn, conv_id)

    deps = MeshContext(
        mode="general",
        conversation_history=conversation_history,
        user_demographics=_user_demographics(user),
    )

    agent_resp = await _call_llm(deps, conv_id)
    if not agent_resp:
        return

    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO messages (conversation_id, sender, content) VALUES ($1, 'agent', $2)",
                conv_id, agent_resp.message,
            )
            # Mark general conversation as completed after response
            await conn.execute(
                """
                UPDATE conversations
                SET status = 'completed', message_count = message_count + 2,
                    updated_at = NOW(), completed_at = NOW()
                WHERE id = $1
                """,
                conv_id,
            )

    _safe_send(phone, agent_resp.message)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _load_history(conn, conv_id) -> list[dict[str, str]]:
    msg_rows = await conn.fetch(
        "SELECT sender, content FROM messages WHERE conversation_id = $1 ORDER BY created_at",
        conv_id,
    )
    return [{"sender": m["sender"], "content": m["content"]} for m in msg_rows]


async def _insert_inbound_user_message(conn, conv_id, body: str, twilio_sid: str) -> bool:
    """
    Inserts an inbound user message. Returns False when twilio_sid has already
    been seen (idempotent duplicate webhook).
    """
    result = await conn.execute(
        """
        INSERT INTO messages (conversation_id, sender, content, twilio_sid)
        VALUES ($1, 'user', $2, $3)
        ON CONFLICT DO NOTHING
        """,
        conv_id,
        body,
        twilio_sid or None,
    )
    return result.endswith("1")


async def _get_or_create_active_onboarding_conversation(user_id, phone: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Serialize conversation creation per user to avoid duplicate active onboarding threads.
            await conn.execute(
                "SELECT pg_advisory_xact_lock(hashtext('user:' || $1::text))",
                str(user_id),
            )
            existing = await conn.fetchrow(
                """
                SELECT *
                FROM conversations
                WHERE user_id = $1
                  AND campaign_id IS NULL
                  AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                user_id,
            )
            if existing:
                return existing

            return await conn.fetchrow(
                """
                INSERT INTO conversations (user_id, phone_number, status)
                VALUES ($1, $2, 'active')
                RETURNING *
                """,
                user_id,
                phone,
            )


def _user_demographics(user) -> dict[str, Any]:
    return {
        "city": user["city"],
        "neighborhood": user["neighborhood"],
        "age_range": user["age_range"],
        "gender": user["gender"],
    }


_DEMOGRAPHICS_WHITELIST = {"city", "neighborhood", "age_range", "gender"}


async def _update_user_demographics(
    conn, user_id, demographics: dict, current_user,
) -> bool:
    """Update user demographics. Returns True if user became onboarded."""
    if not demographics:
        return False

    # Whitelist + only update non-None values
    updates = {
        k: v for k, v in demographics.items()
        if v is not None and k in _DEMOGRAPHICS_WHITELIST
    }
    if not updates:
        return False

    # Build dynamic UPDATE (keys are guaranteed safe via whitelist)
    set_clauses = []
    values = []
    for i, (key, value) in enumerate(updates.items(), start=2):
        set_clauses.append(f"{key} = ${i}")
        values.append(value)

    await conn.execute(
        f"UPDATE users SET {', '.join(set_clauses)} WHERE id = $1",
        user_id, *values,
    )

    # Check if user is now fully onboarded
    # Merge current demographics with updates
    merged = {**_user_demographics(current_user), **updates}
    all_filled = all(merged.get(k) for k in _REQUIRED_DEMOGRAPHICS)

    if all_filled and current_user["status"] != "onboarded":
        await conn.execute(
            "UPDATE users SET status = 'onboarded' WHERE id = $1", user_id
        )
        return True

    return False


async def _call_llm(deps: MeshContext, conv_id) -> Any:
    """Call LLM with semaphore. Returns AgentResponse or None on error."""
    assert _llm_semaphore is not None
    async with _llm_semaphore:
        try:
            return await get_agent_response(deps)
        except Exception:
            logger.exception("Agent failed for conversation=%s", conv_id)
            return None


async def _check_campaign_completion(campaign_id) -> None:
    pool = get_pool()
    row = await pool.fetchrow(
        """
        SELECT c.total_conversations,
               COUNT(*) FILTER (
                   WHERE conv.status IN ('completed', 'declined', 'abandoned', 'expired', 'failed')
               ) AS terminal_count
        FROM campaigns c
        LEFT JOIN conversations conv ON conv.campaign_id = c.id
        WHERE c.id = $1
        GROUP BY c.id
        """,
        campaign_id,
    )
    if row and row["terminal_count"] >= row["total_conversations"] > 0:
        await pool.execute(
            "UPDATE campaigns SET status = 'completed', updated_at = NOW() WHERE id = $1",
            campaign_id,
        )
        logger.info("Campaign %s completed (all conversations terminal)", campaign_id)


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
