import pytest
from flask_wtf.csrf import generate_csrf
import app.database as data
from app.middleware import db
from app.constants import TICKET_STATUSES



@pytest.mark.usefixtures("c")
def test_update_token_details_form_validation_failed(c):
    """
    Test updating ticket details with missing CSRF token"""

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
def test_update_token_details_invalid_status(app,c):
    
    app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with app.test_request_context():
        token = generate_csrf()

    all_tickets = data.Serial.all_clean()

   
    ticket_to_update = all_tickets[3]
    ticket_name = ticket_to_update.name

    url='/update_token_details'
    payload = {
        'ticket_name': ticket_name,
        'status': 'invalid_status',
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
  
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Form validation failed'


@pytest.mark.usefixtures("app","c")
def test_update_token_details_ticket_not_pulled(app,c):
    
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
    
    ticket_to_update.p = False  #Ensure ticket is not pulled
    db.session.commit()
   
    new_status = TICKET_STATUSES[2] #Attended, can also be Processed, that is TICKET_STATUSES[1]

    url='/update_token_details'
    payload = {
        'ticket_name': ticket_name,
        'status': new_status,
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
  
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Ticket must be pulled before processing/attending'


@pytest.mark.usefixtures("app","c")
def test_update_token_details_same_status(app,c):
    
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
   
    new_status = current_status  #Same status

    url='/update_token_details'
    payload = {
        'ticket_name': ticket_name,
        'status': new_status,
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
  
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Ticket is already in the desired status'


@pytest.mark.usefixtures("app","c")
def test_update_token_details_invalid_transition(app,c):
    """
    Processed without being attended
    """
    
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

    #pull the ticket
    ticket_to_update.p = True  
    db.session.commit()
   
    new_status = TICKET_STATUSES[1]  #Processed without being attended

    url='/update_token_details'
    payload = {
        'ticket_name': ticket_name,
        'status': new_status,
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
  
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Ticket must be in process before processing'



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
    print("Current Status:", current_status)
    ticket_to_update.p = True  #Ensure ticket is pulled
    db.session.commit()
   
    new_status = TICKET_STATUSES[2]

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

@pytest.mark.usefixtures("app","c")
def test_check_processing_time_from_timestamps(app,c):
    """
    Test to verify that the processing time is correctly calculated from timestamps.
    """
    app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with app.test_request_context():
        token = generate_csrf()

    all_tickets = data.Serial.all_clean()

   
    ticket_to_update = all_tickets[4]
    ticket_name = ticket_to_update.name

    #Pull the ticket
    ticket_to_update.p = True  
    db.session.commit()
   
    #Update status to Processed
    url='/update_token_details'
    payload = {
        'ticket_name': ticket_name,
        'status': TICKET_STATUSES[2],  #Attended
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    assert json_response['status'] == 'success'
    assert json_response['message'] == 'Ticket updated successfully'

    #Update status to Attended
    payload['status'] = TICKET_STATUSES[1]  #Processed

    resp = c.post(url,json=payload)
    assert resp.status_code == 200

    json_response = resp.get_json()
  
    assert json_response['status'] == 'success'
    assert json_response['message'] == 'Ticket updated successfully'

    # get timestamps
    updated_ticket = data.Serial.query.filter_by(name=ticket_name).first()
    timestamp2 = updated_ticket.timestamp2
    timestamp3 = updated_ticket.timestamp3

    # Calculate processing time
  
    processing_time = (timestamp3 - timestamp2).total_seconds()
    print("Processing time in seconds:", processing_time)
    assert processing_time >= 0  #Processing time should be non-negative
    