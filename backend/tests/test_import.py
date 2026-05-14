from __future__ import annotations

import mailbox
from email.message import EmailMessage
from pathlib import Path

from app.utils.mbox_parser import iter_mbox_messages


async def test_mbox_parser_extracts_attachment_and_metadata(tmp_path):
    mbox_path = tmp_path / 'sample.mbox'
    box = mailbox.mbox(mbox_path)
    msg = EmailMessage()
    msg['From'] = 'legal@company.com'
    msg['To'] = 'sales@company.com'
    msg['Subject'] = 'Urgent NDA review'
    msg['Message-ID'] = '<test-nda@example.com>'
    msg['Date'] = 'Thu, 14 May 2026 10:00:00 +0000'
    msg.set_content('Please review NDA-2026 and liability clause.')
    msg.add_attachment(b'clause excerpt', maintype='application', subtype='octet-stream', filename='nda.txt')
    box.add(msg)
    box.flush()

    parsed = list(iter_mbox_messages(mbox_path))
    assert len(parsed) == 1
    assert parsed[0].message_id == '<test-nda@example.com>'
    assert parsed[0].has_attachments is True
    assert parsed[0].attachments[0].filename == 'nda.txt'


async def test_import_job_endpoint_runs(client, auth_headers, tmp_path):
    mbox_path = tmp_path / 'sample-import.mbox'
    box = mailbox.mbox(mbox_path)
    msg = EmailMessage()
    msg['From'] = 'legal@company.com'
    msg['To'] = 'sales@company.com'
    msg['Subject'] = 'Urgent NDA review'
    msg['Message-ID'] = '<import-nda@example.com>'
    msg['Date'] = 'Thu, 14 May 2026 10:00:00 +0000'
    msg.set_content('Please review NDA-2026 and liability clause.')
    box.add(msg)
    box.flush()

    relative_mbox_path = mbox_path.relative_to(Path('/tmp')).as_posix()
    response = await client.post('/api/import/jobs', headers=auth_headers, json={'mbox_path': relative_mbox_path, 'batch_size': 100})
    assert response.status_code == 200
    job_id = response.json()['id']

    progress = await client.get(f'/api/import/jobs/{job_id}/progress', headers=auth_headers)
    assert progress.status_code == 200
    assert progress.json()['filename'] == 'sample-import.mbox'


async def test_import_job_rejects_non_mbox_files(client, auth_headers, tmp_path):
    invalid_path = tmp_path / 'sample.txt'
    invalid_path.write_text('not an mbox', encoding='utf-8')
    relative_invalid_path = invalid_path.relative_to(Path('/tmp')).as_posix()

    response = await client.post('/api/import/jobs', headers=auth_headers, json={'mbox_path': relative_invalid_path, 'batch_size': 100})

    assert response.status_code == 400
    assert response.json()['detail'] == 'only .mbox import files are supported'
