from __future__ import annotations

import mailbox
from dataclasses import dataclass, field
from email.message import Message
from pathlib import Path
from typing import Iterator

from app.utils.date_utils import parse_email_date
from app.utils.email_utils import detect_auto_reply, detect_forwarded, normalize_subject, split_addresses


@dataclass(slots=True)
class ParsedAttachment:
    filename: str
    content_type: str | None
    payload: bytes


@dataclass(slots=True)
class ParsedEmail:
    message_id: str
    subject: str
    subject_normalized: str
    sender: str
    recipients_to: list[str]
    recipients_cc: list[str]
    recipients_bcc: list[str]
    body_plain: str | None
    body_html: str | None
    sent_at: object | None
    received_at: object | None
    labels: list[str]
    raw_headers: dict[str, str]
    size_bytes: int
    has_attachments: bool
    is_forwarded: bool
    is_auto_reply: bool
    language: str | None
    thread_header_id: str | None
    in_reply_to: str | None
    references: list[str]
    attachments: list[ParsedAttachment] = field(default_factory=list)


def _decode_payload(part: Message) -> str | None:
    payload = part.get_payload(decode=True)
    if payload is None:
        text_payload = part.get_payload()
        return text_payload if isinstance(text_payload, str) else None
    charset = part.get_content_charset() or 'utf-8'
    return payload.decode(charset, errors='replace')


def _extract_bodies(message: Message) -> tuple[str | None, str | None, list[ParsedAttachment]]:
    plain_parts: list[str] = []
    html_parts: list[str] = []
    attachments: list[ParsedAttachment] = []
    if message.is_multipart():
        for part in message.walk():
            content_disposition = (part.get('Content-Disposition') or '').lower()
            content_type = part.get_content_type()
            if 'attachment' in content_disposition:
                attachments.append(
                    ParsedAttachment(
                        filename=part.get_filename() or 'attachment.bin',
                        content_type=content_type,
                        payload=part.get_payload(decode=True) or b'',
                    )
                )
                continue
            if content_type == 'text/plain':
                text = _decode_payload(part)
                if text:
                    plain_parts.append(text)
            elif content_type == 'text/html':
                html = _decode_payload(part)
                if html:
                    html_parts.append(html)
    else:
        content_type = message.get_content_type()
        text = _decode_payload(message)
        if content_type == 'text/html':
            html_parts.append(text or '')
        else:
            plain_parts.append(text or '')
    return ('\n'.join(part for part in plain_parts if part) or None, '\n'.join(part for part in html_parts if part) or None, attachments)


def iter_mbox_messages(mbox_path: str | Path) -> Iterator[ParsedEmail]:
    box = mailbox.mbox(str(mbox_path), create=False)
    for message in box:
        message_id = message.get('Message-ID') or message.get('Message-Id')
        if not message_id:
            continue
        body_plain, body_html, attachments = _extract_bodies(message)
        subject = message.get('Subject') or ''
        raw_headers = {key: str(value) for key, value in message.items()}
        labels = [label.strip() for label in (message.get('X-Gmail-Labels') or '').split(',') if label.strip()]
        references = [item.strip() for item in (message.get('References') or '').split() if item.strip()]
        sender = split_addresses(message.get('From'))
        yield ParsedEmail(
            message_id=message_id.strip(),
            subject=subject,
            subject_normalized=normalize_subject(subject),
            sender=sender[0] if sender else (message.get('From') or '').strip().lower(),
            recipients_to=split_addresses(message.get_all('To')),
            recipients_cc=split_addresses(message.get_all('Cc')),
            recipients_bcc=split_addresses(message.get_all('Bcc')),
            body_plain=body_plain,
            body_html=body_html,
            sent_at=parse_email_date(message.get('Date')),
            received_at=parse_email_date(message.get('Date')),
            labels=labels,
            raw_headers=raw_headers,
            size_bytes=len(message.as_bytes()),
            has_attachments=bool(attachments),
            is_forwarded=detect_forwarded(subject, body_plain),
            is_auto_reply=detect_auto_reply(subject, body_plain),
            language='en',
            thread_header_id=message.get('X-GM-THRID'),
            in_reply_to=message.get('In-Reply-To'),
            references=references,
            attachments=attachments,
        )
