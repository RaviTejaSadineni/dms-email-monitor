from __future__ import annotations


async def test_contract_stage_transition(client, auth_headers):
    create = await client.post(
        '/api/contracts',
        headers=auth_headers,
        json={
            'contract_number': 'NDA-1234',
            'contract_type': 'NDA',
            'parties': ['Company', 'Acme'],
            'current_stage': 'Request',
        },
    )
    assert create.status_code == 201
    contract_id = create.json()['id']

    stage = await client.post(
        f'/api/contracts/{contract_id}/stages',
        headers=auth_headers,
        json={'stage_name': 'Legal Review', 'entered_at': '2026-05-14T10:00:00Z'},
    )
    assert stage.status_code == 201
    assert stage.json()['stage_name'] == 'Legal Review'
