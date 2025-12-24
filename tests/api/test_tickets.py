import sys
import pytest

from app.database import Serial, AuthTokens, Task
from app.utils import get_module_columns
from app.api.constants import LIMIT_PER_CHUNK


BASE = '/api/v1/tickets'

EXPECTED_TICKET_FIELDS = {
    'id',
    'number',
    'timestamp',
    'date',
    'name',
    'status',
    'office_id',
    'task_id',
    'p',
    'n',
}



@pytest.mark.usefixtures('c')
def test_unauthorized_request(c):
    response = c.get(BASE,
                     follow_redirects=True,
                     headers={'Authorization': 'wrong token'})

    assert response.status == '401 UNAUTHORIZED'
    assert response.json.get('message') == 'Authentication is required'


@pytest.mark.usefixtures('c')
def test_list_tickets(c):
    auth_token = AuthTokens.get()
    response = c.get(BASE,
                     follow_redirects=True,
                     headers={'Authorization': auth_token.token})

    assert response.status == '200 OK'
    assert len(response.json) > 0
    assert LIMIT_PER_CHUNK > len(response.json)
    print(get_module_columns(Serial))
    print(response.json[0].keys())
    print(Serial.__module__)
    print(sys.modules[Serial.__module__].__file__)

    #print(id(Serial))
    #print(id(response.json))


    for t in response.json:
        assert Serial.get(t.get('id')) is not None
        #assert all(p in t for p in get_module_columns(Serial)) is True
        assert EXPECTED_TICKET_FIELDS.issubset(t.keys())



@pytest.mark.usefixtures('c')
def test_get_ticket(c):
    ticket = Serial.all_clean().first()
    auth_token = AuthTokens.get()
    response = c.get(f'{BASE}/{ticket.id}',
                     follow_redirects=True,
                     headers={'Authorization': auth_token.token})

    assert response.status == '200 OK'
    assert Serial.get(response.json.get('id')).id == ticket.id
    #assert all(p in response.json for p in get_module_columns(Serial)) is True
    assert EXPECTED_TICKET_FIELDS.issubset(response.json.keys())


@pytest.mark.usefixtures('c')
def test_get_wrong_ticket(c):
    auth_token = AuthTokens.get()
    response = c.get(f'{BASE}/9191919',
                     follow_redirects=True,
                     headers={'Authorization': auth_token.token})

    assert response.status == '404 NOT FOUND'


@pytest.mark.usefixtures('c')
def test_update_ticket(c):
    ticket = Serial.all_clean().first()
    new_name = 'new testing name'
    auth_token = AuthTokens.get()
    response = c.put(f'{BASE}/{ticket.id}',
                     follow_redirects=True,
                     headers={'Authorization': auth_token.token},
                     json={'name': new_name})

    assert response.status == '200 OK'
    assert Serial.get(response.json.get('id')).name == new_name
    #assert all(p in response.json for p in get_module_columns(Serial)) is True
    assert EXPECTED_TICKET_FIELDS.issubset(response.json.keys())


@pytest.mark.usefixtures('c')
def test_delete_ticket(c):
    ticket = Serial.all_clean().first()
    auth_token = AuthTokens.get()
    response = c.delete(f'{BASE}/{ticket.id}',
                        follow_redirects=True,
                        headers={'Authorization': auth_token.token})

    assert response.status == '204 NO CONTENT'
    assert response.data == b''
    assert Serial.get(ticket.id) is None


@pytest.mark.usefixtures('c')
def test_delete_all_tickets(c):
    auth_token = AuthTokens.get()
    response = c.delete(f'{BASE}',
                        follow_redirects=True,
                        headers={'Authorization': auth_token.token})

    assert response.status == '204 NO CONTENT'
    assert response.data == b''
    assert Serial.all_clean().count() == 0


@pytest.mark.usefixtures('c')
def test_generate_ticket(c):
    name = 'new testing name'
    task = Task.get()
    office = task.offices[0]
    auth_token = AuthTokens.get()
    response = c.post(f'{BASE}',
                      follow_redirects=True,
                      headers={'Authorization': auth_token.token},
                      json={'name': name,
                            'task_id': task.id,
                            'office_id': office.id})
    ticket = Serial.get(response.json.get('id'))

    assert response.status == '200 OK'
    assert ticket is not None
    assert ticket.name == name
    assert ticket.task_id == task.id
    assert ticket.office_id == office.id
    #assert all(p in response.json for p in get_module_columns(Serial)) is True
    assert EXPECTED_TICKET_FIELDS.issubset(response.json.keys())


@pytest.mark.usefixtures('c')
def test_pull_ticket(c):
    auth_token = AuthTokens.get()
    response = c.get(f'{BASE}/pull',
                     follow_redirects=True,
                     headers={'Authorization': auth_token.token})
    ticket = Serial.get(response.json.get('id'))

    assert response.status == '200 OK'
    assert ticket is not None
    assert ticket.p is True
    #assert all(p in response.json for p in get_module_columns(Serial)) is True
    assert EXPECTED_TICKET_FIELDS.issubset(response.json.keys())
