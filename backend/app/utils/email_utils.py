from __future__ import annotations

import re
from email.utils import getaddresses

SUBJECT_PREFIX_RE = re.compile(r'^(re|fw|fwd):\s*', re.IGNORECASE)


def split_addresses(values: list[str] | str | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    return [email.strip().lower() for _, email in getaddresses(values) if email]


def normalize_subject(subject: str | None) -> str:
    value = (subject or '').strip()
    while True:
        updated = SUBJECT_PREFIX_RE.sub('', value).strip()
        if updated == value:
            return value.lower()
        value = updated


def detect_auto_reply(subject: str | None, body: str | None) -> bool:
    source = f"{subject or ''} {body or ''}".lower()
    markers = ['out of office', 'automatic reply', 'auto-reply', 'autoreply']
    return any(marker in source for marker in markers)


def detect_forwarded(subject: str | None, body: str | None) -> bool:
    source = f"{subject or ''} {body or ''}".lower()
    return subject is not None and subject.lower().startswith(('fw:', 'fwd:')) or 'forwarded message' in source
