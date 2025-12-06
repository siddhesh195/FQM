import pytest
import app.database as data
from app.middleware import db
from app.constants import TICKET_STATUSES
from flask_wtf.csrf import generate_csrf



@pytest.mark.usefixtures("c")
def test_offices_home(c):
    url='/all_offices_vue'
    resp = c.get(url)
    assert resp.status_code == 200
    assert b"Offices" in resp.data


@pytest.mark.usefixtures("c")
def test_all_offices_tickets(c):
   
    url='/all_offices_tickets'
    resp = c.get(url)
    assert resp.status_code == 200
    
    names=[]
    offices=[]

    json_response = resp.get_json()

    for ticket in json_response:
        names.append(ticket['name'])
        offices.append(ticket['office_name'])
    print(offices)
    assert len(names) == 8
    assert len(offices) == 8


@pytest.mark.usefixtures("c")
def test_pull_ticket_success(c):

    all_tickets = data.Serial.all_clean()

    
    ticket_to_pull = all_tickets[0]
    ticket_name = ticket_to_pull.name
    ticket_id = ticket_to_pull.id
    office_id = ticket_to_pull.office_id

    url='/pull_ticket'
    payload = {
        'ticket_id': ticket_id,
        'office_id': office_id,
        'ticket_name': ticket_name
    }
    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
    assert json_response['status'] == 'success'
    assert json_response['message'] == f'Ticket {ticket_name} pulled successfully'



@pytest.mark.usefixtures("c")
def test_pull_ticket_not_found(c):

    url='/pull_ticket'
    payload = {
        'ticket_id': 9999,
        'office_id': 1,
        'ticket_name': 'NonExistentTicket'
    }
    resp = c.post(url,json=payload)
    assert resp.status_code == 404

    json_response = resp.get_json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Ticket not found'



@pytest.mark.usefixtures("c")
def test_pull_ticket_already_pulled(c):

    all_tickets = data.Serial.all_clean()

    
    ticket_to_pull = all_tickets[1]
    ticket_to_pull.p = True
    db.session.commit()

    ticket_name = ticket_to_pull.name
    ticket_id = ticket_to_pull.id
    office_id = ticket_to_pull.office_id

    url='/pull_ticket'
    payload = {
        'ticket_id': ticket_id,
        'office_id': office_id,
        'ticket_name': ticket_name
    }
    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Ticket already pulled'

    
@pytest.mark.usefixtures("c")
def test_update_token_details_form_validation_failed(c):

    all_tickets = data.Serial.all_clean()

   
    
    ticket_to_update = all_tickets[2]
    ticket_name = ticket_to_update.name

    url='/update_token_details'
    payload = {
        'ticket_name': ticket_name,
        'status': 'completed'
    }
    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == f'Form validation failed'

@pytest.mark.usefixtures("app","c")
def test_update_token_details_no_ticket(app,c):
    
    app.config["WTF_CSRF_ENABLED"] = True

    #Get correct CSRF token from session
    with app.test_request_context():
        token = generate_csrf()

    url='/update_token_details'

    payload = {
        'ticket_name': 'NonExistentTicket',
        'status': 'completed'
    }
    headers = {
        'X-CSRFToken': token
    }
    resp = c.post(url,json=payload,headers=headers)
    assert resp.status_code == 200

    json_response = resp.get_json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Ticket not found'


@pytest.mark.usefixtures("app","c")
def test_update_token_details_success(app,c):
    
    #Enable CSRF protection for this test
    app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with app.test_request_context():
        token = generate_csrf()

    all_tickets = data.Serial.all_clean()

   
    ticket_to_update = all_tickets[3]
    ticket_name = ticket_to_update.name
    current_status = ticket_to_update.status
    ticket_to_update.p = True  #Ensure ticket is pulled
    db.session.commit()
    new_status = None
    for status in TICKET_STATUSES:
        if status != current_status:
            new_status = status
            break

    url='/update_token_details'
    payload = {
        'ticket_name': ticket_name,
        'status': new_status,
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
  
    assert json_response['status'] == 'success'
    assert json_response['message'] == 'Ticket updated successfully'

    #Verify that ticket status is updated in database
    updated_ticket = data.Serial.query.filter_by(name=ticket_name).first()
    assert updated_ticket.status == new_status


@pytest.mark.usefixtures("c")
def test_get_all_active_tickets(c):

    url='/get_number_of_active_tickets'
    resp = c.get(url)
    assert resp.status_code == 200

    json_response = resp.get_json()
    assert 'active_tickets' in json_response
    assert isinstance(json_response['active_tickets'], int)

    current_active_tickets_count = json_response['active_tickets']

    #pull a ticket to change active tickets count
    all_tickets = data.Serial.all_clean()

    ticket_to_pull =None
    for ticket in all_tickets:
        if not ticket.p:
            ticket_to_pull = ticket
            break
    if not ticket_to_pull:
        pytest.skip("No available ticket to pull for testing.")
    ticket_id = ticket_to_pull.id
    ticket_name = ticket_to_pull.name
    office_id = ticket_to_pull.office_id
    pull_url='/pull_ticket'
    pull_payload = {
        'ticket_id': ticket_id,
        'office_id': office_id,
        'ticket_name': ticket_name
    }
    pull_resp = c.post(pull_url,json=pull_payload)
    assert pull_resp.status_code == 200
    pull_json_response = pull_resp.get_json()
    assert pull_json_response['status'] == 'success'

    #Get active tickets count again
    resp_after_pull = c.get(url)
    assert resp_after_pull.status_code == 200

    json_response_after_pull = resp_after_pull.get_json()
    assert 'active_tickets' in json_response_after_pull
    assert isinstance(json_response_after_pull['active_tickets'], int)

    assert json_response_after_pull['active_tickets'] == current_active_tickets_count - 1

    


    


