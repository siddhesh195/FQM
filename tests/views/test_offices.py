import pytest
import app.database as data
from app.middleware import db
from flask_wtf.csrf import generate_csrf



@pytest.mark.usefixtures("c")
def test_offices_home_admin_login(c,monkeypatch):
    class user:
        def __init__(self):
            self.role_id = 1  #Admin role
    current_user = user()
    monkeypatch.setattr('app.views.offices.current_user', current_user)
    url='/all_offices_vue'
    resp = c.get(url)
    assert resp.status_code == 200
    assert b"Offices" in resp.data


@pytest.mark.usefixtures("c")
def test_offices_home_non_admin_login_failure(c,monkeypatch):
    
    class user:
        def __init__(self):
            self.role_id = 2  #non admin role_id
   
    current_user = user()
    monkeypatch.setattr('app.views.offices.current_user', current_user)
    url='/all_offices_vue'
    resp = c.get(url)
    assert resp.status_code == 400
    assert b"Office ID is required for Non Admins" in resp.data


@pytest.mark.usefixtures("c")
def test_offices_home_operator_access(c,monkeypatch):
    class user:
        def __init__(self,id):
            self.role_id = 3  #Operator role_id
            self.id =id
    
    #create a new User
    
    new_user= data.User(name="Operator User",password="password", role_id=3)

    db.session.add(new_user)
    db.session.commit()
    
    to_be_operator_user = data.User.query.filter_by(name="Operator User").first()
    assert to_be_operator_user is not None
    
    # monkeypatch current_user to be the created user
    current_user = user(to_be_operator_user.id)
    monkeypatch.setattr('app.views.offices.current_user', current_user)

    #create two new offices

    office1 = data.Office(name="ABC Office", prefix="A")
    office2 = data.Office(name="XYZ Office", prefix="X")
    db.session.add(office1)
    db.session.add(office2)
    db.session.commit()
    office_abc = data.Office.query.filter_by(name="ABC Office").first()
    office_xyz = data.Office.query.filter_by(name="XYZ Office").first()
    assert office_abc is not None
    assert office_xyz is not None
    office_abc_id = office_abc.id


    #assign operator to one office
    operator_user = data.Operators(id=to_be_operator_user.id, office_id=office_abc.id)
   
    db.session.add(operator_user)
    db.session.commit()


    operator = data.Operators.query.filter_by(id=current_user.id).first()
    assert operator is not None
    
    # send wrong office id to access
    url=f'/all_offices_vue/{office_abc_id}'
    resp = c.get(url)
   
    assert resp.status_code == 200
    assert b"Offices" in resp.data


@pytest.mark.usefixtures("c")
def test_offices_home_operator_failure(c,monkeypatch):
    class user:
        def __init__(self,id):
            self.role_id = 3  #Operator role_id
            self.id =id
    
    #create a new User
    
    new_user= data.User(name="Operator User",password="password", role_id=3)

    db.session.add(new_user)
    db.session.commit()
    
    to_be_operator_user = data.User.query.filter_by(name="Operator User").first()
    assert to_be_operator_user is not None
    
    # monkeypatch current_user to be the created user
    current_user = user(to_be_operator_user.id)
    monkeypatch.setattr('app.views.offices.current_user', current_user)

    #create two new offices

    office1 = data.Office(name="ABC Office", prefix="A")
    office2 = data.Office(name="XYZ Office", prefix="X")
    db.session.add(office1)
    db.session.add(office2)
    db.session.commit()
    office_abc = data.Office.query.filter_by(name="ABC Office").first()
    office_xyz = data.Office.query.filter_by(name="XYZ Office").first()
    assert office_abc is not None
    assert office_xyz is not None
    office_abc_id = office_abc.id
    office_xyz_id = office_xyz.id


    #assign operator to one office
    operator_user = data.Operators(id=to_be_operator_user.id, office_id=office_abc.id)
   
    db.session.add(operator_user)
    db.session.commit()


    operator = data.Operators.query.filter_by(id=current_user.id).first()
    assert operator is not None
    
    url=f'/all_offices_vue/{office_xyz_id}'
    resp = c.get(url)
    json= resp.get_json()
    assert resp.status_code == 403
    assert json['status'] == 'error'
    assert json['message'] == 'Unauthorized access to this office'
   
@pytest.mark.usefixtures("c")
def test_offices_home_non_existent_office(c,monkeypatch):
    class user:
        def __init__(self,id):
            self.role_id = 3  #Operator role_id
            self.id =id
    
    #create a new User
    
    new_user= data.User(name="Operator User",password="password", role_id=3)

    db.session.add(new_user)
    db.session.commit()
    
    to_be_operator_user = data.User.query.filter_by(name="Operator User").first()
    assert to_be_operator_user is not None
    
    # monkeypatch current_user to be the created user
    current_user = user(to_be_operator_user.id)
    monkeypatch.setattr('app.views.offices.current_user', current_user)

    #create two new offices

    office1 = data.Office(name="ABC Office", prefix="A")
    office2 = data.Office(name="XYZ Office", prefix="X")
    db.session.add(office1)
    db.session.add(office2)
    db.session.commit()
    office_abc = data.Office.query.filter_by(name="ABC Office").first()
    office_xyz = data.Office.query.filter_by(name="XYZ Office").first()
    assert office_abc is not None
    assert office_xyz is not None
    office_abc_id = office_abc.id
    office_xyz_id = office_xyz.id


    #assign operator to one office
    operator_user = data.Operators(id=to_be_operator_user.id, office_id=office_abc.id)
   
    db.session.add(operator_user)
    db.session.commit()


    operator = data.Operators.query.filter_by(id=current_user.id).first()
    assert operator is not None
    non_existent_office_id = 9999
    url=f'/all_offices_vue/{non_existent_office_id}'
    resp = c.get(url)
    json= resp.get_json()
    assert resp.status_code == 404
    assert json['status'] == 'error'
    assert json['message'] == 'Office not found'
   

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


@pytest.mark.usefixtures("flask_app","c")
def test_add_offices_form_validation_failed_no_csrf(flask_app,c,monkeypatch):

    flask_app.config["WTF_CSRF_ENABLED"] = True
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


@pytest.mark.usefixtures("flask_app","c")
def test_add_offices_form_validation_pass_and_failed_due_to_name_length(flask_app,c,monkeypatch):
    flask_app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with flask_app.test_request_context():
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
   


@pytest.mark.usefixtures("flask_app","c")
def test_add_offices_form_validation_failed_due_to_wrong_prefix(flask_app,c,monkeypatch):
    flask_app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with flask_app.test_request_context():
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
  
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Form validation failed'

    #Verify that office is not added in database
    added_office = data.Office.query.filter_by(name='New Test Office').first()
    assert added_office is None
    


@pytest.mark.usefixtures("flask_app","c")
def test_add_offices_office_name_exists(flask_app,c,monkeypatch):

    flask_app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with flask_app.test_request_context():
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

   


@pytest.mark.usefixtures("flask_app","c")
def test_add_offices_unauthorized_access(flask_app,c,monkeypatch):

    flask_app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with flask_app.test_request_context():
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

@pytest.mark.usefixtures("flask_app","c")
def test_add_offices_success(flask_app,c,monkeypatch):

    flask_app.config["WTF_CSRF_ENABLED"] = True

    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with flask_app.test_request_context():
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