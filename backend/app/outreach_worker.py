import asyncio
import json
import logging

from .conversation_agent import get_agent_response
from .db import get_pool
from .twilio_client import send_whatsapp

logger = logging.getLogger("backend.outreach_worker")

_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None

POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 10


def start_outreach_worker() -> None:
    global _task, _stop_event
    _stop_event = asyncio.Event()
    _task = asyncio.create_task(_worker_loop())
    logger.info("Outreach worker started")


def stop_outreach_worker() -> None:
    global _task
    if _stop_event:
        _stop_event.set()
    if _task:
        _task.cancel()
        _task = None
    logger.info("Outreach worker stopped")


async def _worker_loop() -> None:
    assert _stop_event is not None
    while not _stop_event.is_set():
        try:
            processed = await _process_batch()
            if processed == 0:
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Outreach worker error")
            await asyncio.sleep(POLL_INTERVAL_SECONDS)


async def _process_batch() -> int:
    pool = get_pool()

    # Claim a batch of pending outreach items that are due
    rows = await pool.fetch(
        """
        UPDATE outreach_queue
        SET status = 'sent'
        WHERE id IN (
            SELECT id FROM outreach_queue
            WHERE status = 'pending' AND scheduled_at <= NOW()
            ORDER BY scheduled_at
            LIMIT $1
            FOR UPDATE SKIP LOCKED
        )
        RETURNING id, conversation_id
        """,
        BATCH_SIZE,
    )

    if not rows:
        return 0

    tasks = [_send_opening(row["id"], row["conversation_id"]) for row in rows]
    await asyncio.gather(*tasks, return_exceptions=True)
    return len(rows)


async def _send_opening(queue_id, conversation_id) -> None:
    pool = get_pool()

    try:
        # Load conversation + campaign
        conv = await pool.fetchrow(
            """
            SELECT c.*, cam.research_brief, cam.extraction_schema,
                   cam.system_prompt_override
            FROM conversations c
            JOIN campaigns cam ON c.campaign_id = cam.id
            WHERE c.id = $1
            """,
            conversation_id,
        )
        if not conv:
            logger.warning("Conversation %s not found for outreach", conversation_id)
            return

        extraction_schema = conv["extraction_schema"]
        if isinstance(extraction_schema, str):
            extraction_schema = json.loads(extraction_schema)

        # Generate opening message via agent (empty history)
        agent_resp = await get_agent_response(
            research_brief=conv["research_brief"],
            extraction_schema=extraction_schema,
            extracted_data={},
            conversation_history=[],
            system_prompt_override=conv["system_prompt_override"],
        )

        # Send via Twilio
        phone = conv["phone_number"]
        to = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
        sid = send_whatsapp(to, agent_resp.message)
        logger.info("Outreach sent to %s, sid=%s", phone, sid)

        # Persist agent message and update conversation
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO messages (conversation_id, sender, content, twilio_sid)
                    VALUES ($1, 'agent', $2, $3)
                    """,
                    conversation_id,
                    agent_resp.message,
                    sid,
                )
                await conn.execute(
                    """
                    UPDATE conversations
                    SET status = 'outreach_sent', message_count = 1, updated_at = NOW()
                    WHERE id = $1
                    """,
                    conversation_id,
                )
                await conn.execute(
                    "UPDATE outreach_queue SET sent_at = NOW() WHERE id = $1",
                    queue_id,
                )

    except Exception as e:
        logger.exception("Failed outreach for conversation %s", conversation_id)
        await pool.execute(
            "UPDATE outreach_queue SET status = 'failed', error = $2 WHERE id = $1",
            queue_id,
            str(e),
        )
        await pool.execute(
            "UPDATE conversations SET status = 'failed', updated_at = NOW() WHERE id = $1",
            conversation_id,
        )
