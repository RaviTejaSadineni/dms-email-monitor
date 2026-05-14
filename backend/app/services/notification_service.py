from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def send_priority_alert(subject: str, recipient: str) -> None:
    logger.info('Priority alert queued for %s: %s', recipient, subject)
