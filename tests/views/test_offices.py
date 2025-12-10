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

    
@pytest.mark.usefixtures("c")
def test_pull_next_ticket(c):
    #create new office
    new_office = data.Office(name="Test Office for Ticket Pull")
    db.session.add(new_office)
    db.session.commit()
    office_id = new_office.id

    #create new task
    office= data.Office.get(office_id)
    new_task = data.Task(name="Test Task for Ticket Pull")
    db.session.add(new_task)
    db.session.commit()

    #attach task to office
    task = data.Task.query.filter_by(name="Test Task for Ticket Pull").first()
    office.tasks.append(task)
    db.session.commit()
    task_id = task.id
    
    
    #create few tickets with different timestamps
    import datetime
    now = datetime.datetime.utcnow()
    ticket_names = []
    for i in range(3):
        ticket,exception = data.Serial.create_new_ticket(office=office,task=task,name_or_number=f"TestTicket{i+1}")
        ticket_names.append(ticket.name)
        if not exception:
            ticket.timestamp = now + datetime.timedelta(minutes=i)
            db.session.commit()
    
    #confirm tickets are created
    all_tickets = data.Serial.query.filter_by(office_id=office_id, task_id=task_id).all()
    assert len(all_tickets) == 3

    url='/pull_next_ticket'

    payload = {
        'o_id': task_id,
        'ofc_id': office_id
    }
    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
 
    assert json_response['status'] == 'success'
    assert json_response['message'] == f'Ticket {ticket_names[0]} pulled successfully'
    assert json_response['ticket_name'] == ticket_names[0]


@pytest.mark.usefixtures("app","c")
def test_add_offices_form_validation_failed_no_csrf(app,c,monkeypatch):

    app.config["WTF_CSRF_ENABLED"] = True
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices.current_user', current_user)

    url='/add_office'
    
    #Test adding a new office
    payload = {
        'name': 'New Test Office',
        'prefix': 'N'
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Form validation failed'


@pytest.mark.usefixtures("app","c")
def test_add_offices_form_validation_pass_and_failed_due_to_name_length(app,c,monkeypatch):
    app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with app.test_request_context():
        token = generate_csrf()

    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices.current_user', current_user)
    name2=""
    for _ in range(300):
        name2 += "A"
    name=name2+"A"  #301 characters

    
    url='/add_office'
    
    #Test adding a new office
    payload = {
        'name': name,
        'prefix': 'A',
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
  
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Form validation failed'

    #Verify that office is not added in database
    added_office = data.Office.query.filter_by(name=name).first()
    assert added_office is None

    payload2 = {
        'name': name2,
        'prefix': 'A',
        'csrf_token': token
    }
    resp2 = c.post(url,json=payload2)
    assert resp2.status_code == 200
    json_response2 = resp2.get_json()
    
    assert json_response2['status'] == 'success'
    assert json_response2['message'] == 'Office added successfully'

    #Verify that office is added in database
    added_office2 = data.Office.query.filter_by(name=name2).first()
    assert added_office2 is not None
   


@pytest.mark.usefixtures("app","c")
def test_add_offices_form_validation_failed_due_to_wrong_prefix(app,c,monkeypatch):
    app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with app.test_request_context():
        token = generate_csrf()

    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices.current_user', current_user)

    url='/add_office'
    
    #Test adding a new office
    #wrong prefix
    #prefix should only be from form choices
    payload = {
        'name': 'New Test Office',
        'prefix': 'NT',
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    print(json_response)
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Form validation failed'

    #Verify that office is not added in database
    added_office = data.Office.query.filter_by(name='New Test Office').first()
    assert added_office is None
    


@pytest.mark.usefixtures("app","c")
def test_add_offices_office_name_exists(app,c,monkeypatch):

    app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with app.test_request_context():
        token = generate_csrf()

    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices.current_user', current_user)

    #Create an office to test duplicate name
    existing_office = data.Office(name="Existing Office", prefix="E")
    db.session.add(existing_office)
    db.session.commit()

    url='/add_office'
    
    #Test adding a new office with existing name but different prefix
    # same prefix will cause form validation error
    payload = {
        'name': 'Existing Office',
        'prefix': 'A',
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Office name already exists'

   


@pytest.mark.usefixtures("app","c")
def test_add_offices_unauthorized_access(app,c,monkeypatch):

    app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with app.test_request_context():
        token = generate_csrf()

    class user:
        def __init__(self):
            self.role_id = 2  #Non-admin role
    current_user = user()
    monkeypatch.setattr('app.views.offices.current_user', current_user)

    url='/add_office'
    
    #Test adding a new office
    payload = {
        'name': 'Another Test Office',
        'prefix': 'AT',
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Unauthorized access'

@pytest.mark.usefixtures("app","c")
def test_add_offices_success(app,c,monkeypatch):

    app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with app.test_request_context():
        token = generate_csrf()

    class user:
        def __init__(self):
            self.role_id = 1  #Admin role
    current_user = user()
    monkeypatch.setattr('app.views.offices.current_user', current_user)

    url='/add_office'
    
    #Test adding a new office
    payload = {
        'name': 'Test Office',
        'prefix': 'T',
        'csrf_token': token
    }

    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    assert json_response['status'] == 'success'
    assert json_response['message'] == 'Office added successfully'

    #Verify that office is added in database
    added_office = data.Office.query.filter_by(name='Test Office').first()
    assert added_office is not None
    assert added_office.name == 'Test Office'
    assert added_office.prefix == 'T'