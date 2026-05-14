from __future__ import annotations

import mailbox
from email.message import EmailMessage
from pathlib import Path


async def test_analytics_summary_returns_metrics(client, auth_headers, tmp_path):
    mbox_path = tmp_path / 'analytics.mbox'
    box = mailbox.mbox(mbox_path)
    msg = EmailMessage()
    msg['From'] = 'legal@company.com'
    msg['To'] = 'sales@company.com'
    msg['Subject'] = 'Urgent NDA review'
    msg['Message-ID'] = '<analytics@example.com>'
    msg['Date'] = 'Thu, 14 May 2026 10:00:00 +0000'
    msg.set_content('Please review NDA-2026 liability clause and payment terms.')
    box.add(msg)
    box.flush()
    relative_mbox_path = mbox_path.relative_to(Path('/tmp')).as_posix()
    await client.post('/api/import/jobs', headers=auth_headers, json={'mbox_path': relative_mbox_path, 'batch_size': 100})

    response = await client.get('/api/analytics/summary', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()['metrics']) >= 1
