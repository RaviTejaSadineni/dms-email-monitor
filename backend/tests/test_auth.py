from __future__ import annotations


async def test_register_login_and_me(client):
    register = await client.post(
        '/api/auth/register',
        json={'email': 'analyst@example.com', 'password': 'password123', 'full_name': 'Analyst User'},
    )
    assert register.status_code == 201
    token = register.json()['access_token']

    login = await client.post('/api/auth/login', json={'email': 'analyst@example.com', 'password': 'password123'})
    assert login.status_code == 200
    assert login.json()['token_type'] == 'bearer'

    me = await client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert me.status_code == 200
    assert me.json()['email'] == 'analyst@example.com'
