from __future__ import annotations

import mailbox
from email.message import EmailMessage
from pathlib import Path


async def test_email_listing_filters_work(client, auth_headers, tmp_path):
    mbox_path = tmp_path / 'emails.mbox'
    box = mailbox.mbox(mbox_path)
    for idx, subject in enumerate(['Urgent NDA review', 'Finance review update'], start=1):
        msg = EmailMessage()
        msg['From'] = 'legal@company.com' if idx == 1 else 'finance@company.com'
        msg['To'] = 'sales@company.com'
        msg['Subject'] = subject
        msg['Message-ID'] = f'<email-{idx}@example.com>'
        msg['Date'] = 'Thu, 14 May 2026 10:00:00 +0000'
        msg.set_content(subject)
        box.add(msg)
    box.flush()
    relative_mbox_path = mbox_path.relative_to(Path('/tmp')).as_posix()
    await client.post('/api/import/jobs', headers=auth_headers, json={'mbox_path': relative_mbox_path, 'batch_size': 100})

    response = await client.get('/api/emails?priority=P1', headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['pagination']['total'] >= 1
