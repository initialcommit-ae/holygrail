import asyncio
import logging

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

    tasks = [_send_bounty(row["id"], row["conversation_id"]) for row in rows]
    await asyncio.gather(*tasks, return_exceptions=True)
    return len(rows)


async def _send_bounty(queue_id, conversation_id) -> None:
    pool = get_pool()

    try:
        # Load conversation + campaign + user
        conv = await pool.fetchrow(
            """
            SELECT c.*, cam.research_brief, cam.reward_text,
                   u.status AS user_status
            FROM conversations c
            JOIN campaigns cam ON c.campaign_id = cam.id
            JOIN users u ON c.user_id = u.id
            WHERE c.id = $1
            """,
            conversation_id,
        )
        if not conv:
            logger.warning("Conversation %s not found for outreach", conversation_id)
            return

        user_id = conv["user_id"]
        phone = conv["phone_number"]

        # Advisory lock per user — serializes bounty sends so two concurrent
        # sends for the same user can't both pass the sacred side quest check.
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "SELECT pg_advisory_xact_lock(hashtext('bounty:' || $1::text))",
                    str(user_id),
                )

                # Sacred side quest check (now race-free under lock):
                # if user has another active/bounty_sent conversation, hold off
                conflicting = await conn.fetchval(
                    """
                    SELECT id FROM conversations
                    WHERE user_id = $1
                      AND id != $2
                      AND status IN ('active', 'bounty_sent')
                    LIMIT 1
                    """,
                    user_id,
                    conversation_id,
                )
                if conflicting:
                    # Revert queue item to pending — will be retried next poll
                    await conn.execute(
                        "UPDATE outreach_queue SET status = 'pending' WHERE id = $1",
                        queue_id,
                    )
                    logger.info(
                        "Sacred side quest: user %s busy, holding bounty for conv %s",
                        user_id, conversation_id,
                    )
                    return

                # Build templated bounty message (no LLM call)
                brief_summary = conv["research_brief"] or "a quick research chat"
                reward_text = conv["reward_text"] or "a reward"
                user_status = conv["user_status"]

                if user_status == "onboarded":
                    message = (
                        f"🎯 New bounty: {brief_summary}\n"
                        f"~5 min · {reward_text}\n"
                        "Reply 'go' to start!"
                    )
                else:
                    message = (
                        "Hey! This is MeshAI — we pay people for quick "
                        "research chats on WhatsApp. 💰\n\n"
                        f"🎯 Your first bounty: {brief_summary}\n"
                        f"~5 min · {reward_text}\n"
                        "Reply 'go' to start!"
                    )

                # Send via Twilio
                to = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
                sid = send_whatsapp(to, message)
                logger.info("Bounty sent to %s, sid=%s", phone, sid)

                # Persist agent message and update conversation to bounty_sent
                await conn.execute(
                    """
                    INSERT INTO messages (conversation_id, sender, content, twilio_sid)
                    VALUES ($1, 'agent', $2, $3)
                    """,
                    conversation_id,
                    message,
                    sid,
                )
                await conn.execute(
                    """
                    UPDATE conversations
                    SET status = 'bounty_sent', message_count = 1, updated_at = NOW()
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
        campaign_id = await pool.fetchval(
            "SELECT campaign_id FROM conversations WHERE id = $1",
            conversation_id,
        )
        if campaign_id:
            await _check_campaign_completion(pool, campaign_id)


async def _check_campaign_completion(pool, campaign_id) -> None:
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
