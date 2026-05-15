from __future__ import annotations

import mailbox
from email.message import EmailMessage
from pathlib import Path

from app.database import AsyncSessionLocal
from app.models.analytics import ImportJob
from app.services import import_service
from app.utils import mbox_parser
from app.utils.mbox_parser import count_mbox_messages, iter_mbox_messages


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


async def test_import_job_upload_endpoint_runs(client, auth_headers, tmp_path):
    mbox_path = tmp_path / 'uploaded-import.mbox'
    box = mailbox.mbox(mbox_path)
    msg = EmailMessage()
    msg['From'] = 'legal@company.com'
    msg['To'] = 'sales@company.com'
    msg['Subject'] = 'Upload import'
    msg['Message-ID'] = '<upload-import@example.com>'
    msg['Date'] = 'Thu, 14 May 2026 10:00:00 +0000'
    msg.set_content('Please review uploaded mbox import.')
    box.add(msg)
    box.flush()

    with mbox_path.open('rb') as uploaded_file:
        response = await client.post(
            '/api/import/upload',
            headers=auth_headers,
            files={'file': ('uploaded-import.mbox', uploaded_file, 'application/mbox')},
            data={'batch_size': '100'},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload['filename'] == 'uploaded-import.mbox'
    assert payload['file_size_bytes'] > 0

    progress = await client.get(f"/api/import/jobs/{payload['id']}/progress", headers=auth_headers)
    assert progress.status_code == 200
    assert progress.json()['filename'] == 'uploaded-import.mbox'


async def test_import_job_rejects_non_mbox_files(client, auth_headers, tmp_path):
    invalid_path = tmp_path / 'sample.txt'
    invalid_path.write_text('not an mbox', encoding='utf-8')
    relative_invalid_path = invalid_path.relative_to(Path('/tmp')).as_posix()

    response = await client.post('/api/import/jobs', headers=auth_headers, json={'mbox_path': relative_invalid_path, 'batch_size': 100})

    assert response.status_code == 400
    assert response.json()['detail'] == 'only .mbox import files are supported'


async def test_import_job_upload_rejects_non_mbox_files(client, auth_headers, tmp_path):
    invalid_path = tmp_path / 'uploaded.txt'
    invalid_path.write_text('not an mbox', encoding='utf-8')

    with invalid_path.open('rb') as uploaded_file:
        response = await client.post(
            '/api/import/upload',
            headers=auth_headers,
            files={'file': ('uploaded.txt', uploaded_file, 'text/plain')},
            data={'batch_size': '100'},
        )

    assert response.status_code == 400
    assert response.json()['detail'] == 'only .mbox import files are supported'


async def test_count_mbox_messages_uses_fast_scan(tmp_path):
    mbox_path = tmp_path / 'count-test.mbox'
    box = mailbox.mbox(mbox_path)
    for idx in range(2):
        msg = EmailMessage()
        msg['From'] = 'legal@company.com'
        msg['To'] = 'sales@company.com'
        msg['Subject'] = f'Email {idx}'
        msg['Message-ID'] = f'<count-{idx}@example.com>'
        msg['Date'] = 'Thu, 14 May 2026 10:00:00 +0000'
        msg.set_content('body')
        box.add(msg)
    box.flush()

    assert count_mbox_messages(mbox_path) == 2


async def test_iter_mbox_messages_skips_malformed_message(tmp_path, monkeypatch):
    mbox_path = tmp_path / 'malformed.mbox'
    box = mailbox.mbox(mbox_path)

    first = EmailMessage()
    first['From'] = 'legal@company.com'
    first['To'] = 'sales@company.com'
    first['Subject'] = 'Good email'
    first['Message-ID'] = '<good@example.com>'
    first['Date'] = 'Thu, 14 May 2026 10:00:00 +0000'
    first.set_content('good')
    box.add(first)

    second = EmailMessage()
    second['From'] = 'legal@company.com'
    second['To'] = 'sales@company.com'
    second['Subject'] = 'Bad email'
    second['Message-ID'] = '<bad@example.com>'
    second['Date'] = 'Thu, 14 May 2026 10:00:00 +0000'
    second.set_content('bad')
    box.add(second)
    box.flush()

    original_extract = mbox_parser._extract_bodies

    def flaky_extract(message):
        if message.get('Subject') == 'Bad email':
            raise ValueError('corrupted message')
        return original_extract(message)

    monkeypatch.setattr(mbox_parser, '_extract_bodies', flaky_extract)

    parsed = list(iter_mbox_messages(mbox_path))
    assert len(parsed) == 1
    assert parsed[0].message_id == '<good@example.com>'


async def test_process_import_job_marks_failed_on_unhandled_error(tmp_path, monkeypatch):
    mbox_path = tmp_path / 'failure.mbox'
    mbox_path.write_text('', encoding='utf-8')

    async with AsyncSessionLocal() as session:
        job = ImportJob(
            user_id=None,
            filename='failure.mbox',
            file_size_bytes=0,
            status='queued',
            total_emails=0,
            processed_count=0,
            error_count=0,
            started_at=None,
            completed_at=None,
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        job_id = job.id

    def raise_memory_error(_path):
        raise MemoryError('out of memory')

    monkeypatch.setattr(import_service, 'count_mbox_messages', raise_memory_error)

    await import_service.process_import_job(job_id, str(mbox_path), 100)

    async with AsyncSessionLocal() as session:
        failed = await session.get(ImportJob, job_id)
        assert failed is not None
        assert failed.status == 'failed'
        assert failed.error_count == 1
        assert failed.errors[-1]['batch_start'] == -1
        assert 'out of memory' in failed.errors[-1]['error']
