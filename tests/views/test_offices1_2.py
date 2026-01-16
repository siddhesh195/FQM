import pytest
import app.database as data
from app.middleware import db
from tests.conftest import fill_tickets


@pytest.mark.usefixtures("c")
def test_pull_next_ticket_no_office_id(c):
    url='/pull_next_ticket'

    payload = {
        'o_id': 1,
        'ofc_id': None
    }
    resp = c.post(url,json=payload)
   
    json_response = resp.get_json()
 
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Office ID is required'

@pytest.mark.usefixtures("c")
def test_pull_next_ticket_office_not_found(c):
    url='/pull_next_ticket'

    payload = {
        'o_id': 1,
        'ofc_id': 9999
    }
    resp = c.post(url,json=payload)
   
    json_response = resp.get_json()
 
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'Office not found'

@pytest.mark.usefixtures("c")
def test_pull_next_ticket_no_tickets_available(c):
    """
    No tickets available for that task in a specific office
    """
    #create new office
    new_office = data.Office(name="Test Office No Tickets")
    db.session.add(new_office)
    db.session.commit()
    office_id = new_office.id

    #create new task
    office= data.Office.get(office_id)
    new_task = data.Task(name="Test Task No Tickets")
    db.session.add(new_task)
    db.session.commit()

    #attach task to office
    task = data.Task.query.filter_by(name="Test Task No Tickets").first()
    office.tasks.append(task)
    db.session.commit()
    task_id = task.id
    
    url='/pull_next_ticket'

    payload = {
        'task_id': task_id,
        'ofc_id': office_id
    }
    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
   
    assert json_response['status'] == 'error'
    assert json_response['message'] == 'No tickets available to pull'
    

    
@pytest.mark.usefixtures("c")
def test_pull_next_ticket_success_both_task_and_office_id(c):
    """
    Pull by both task id and office id
    
    """
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
        'task_id': task_id,
        'ofc_id': office_id
    }
    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
 
    assert json_response['status'] == 'success'
    assert json_response['message'] == f'Ticket {ticket_names[0]} pulled successfully'
    assert json_response['ticket_name'] == ticket_names[0]

@pytest.mark.usefixtures("c")
def test_pull_next_ticket_success_no_ids(c):
    """
    Pull next ticket with no task id and no office id
    
    """
    url='/pull_next_ticket'

    payload = {
        'task_id': None,
        'ofc_id': None,
        'global_pull': True
    }
    #first clear existing tickets
    data.Serial.all_clean().delete()
    db.session.commit()

    
    # create two offices
    office1 = data.Office(name="Office 1 for No ID Pull")
    office2 = data.Office(name="Office 2 for No ID Pull")
    db.session.add(office1)
    db.session.add(office2)
    db.session.commit()

    # create a task and attach to both offices
    task1 = data.Task(name="Task 1 for No ID Pull")
    db.session.add(task1)
    db.session.commit()

    office1.tasks.append(task1)
    office2.tasks.append(task1)
    db.session.commit()

    # create few tickets in both offices in interleaved manner
    import datetime
    now = datetime.datetime.utcnow()
    ticket_names = []
    for i in range(2):
        ticket1,exception1 = data.Serial.create_new_ticket(office=office1,task=task1,name_or_number=f"NoIDTicket_O1_{i+1}")
        ticket2,exception2 = data.Serial.create_new_ticket(office=office2,task=task1,name_or_number=f"NoIDTicket_O2_{i+1}")
        ticket_names.append(ticket1.name)
        ticket_names.append(ticket2.name)
        if not exception1:
            ticket1.timestamp = now + datetime.timedelta(minutes=i*2)
            db.session.commit()
        if not exception2:
            ticket2.timestamp = now + datetime.timedelta(minutes=i*2 + 1)
            db.session.commit()
    # confirm tickets are created
    all_tickets_office1 = data.Serial.query.filter_by(office_id=office1.id, task_id=task1.id).all()
    all_tickets_office2 = data.Serial.query.filter_by(office_id=office2.id, task_id=task1.id).all()
    assert len(all_tickets_office1) == 2
    assert len(all_tickets_office2) == 2

    # now pull next ticket with no ids
    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()

    assert json_response['status'] == 'success'
    assert json_response['message'] == f'Ticket {ticket_names[0]} pulled successfully'
    assert json_response['ticket_name'] == ticket_names[0]

    #pull again to get second ticket
    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    assert json_response['status'] == 'success'
    assert json_response['message'] == f'Ticket {ticket_names[1]} pulled successfully'
    assert json_response['ticket_name'] == ticket_names[1]


@pytest.mark.usefixtures("c")
def test_pull_next_ticket_success_only_office_id(c):
    """
    Pull next ticket with only office id
    
    """
    
    
    #create two new offices
    office1 = data.Office(name="Office 1 for Only Office ID Pull")
    office2 = data.Office(name="Office 2 for Only Office ID Pull")
    db.session.add(office1)
    db.session.add(office2)
    db.session.commit()

    #create new task and attach to both offices
    new_task = data.Task(name="Task for Only Office ID Pull")
    db.session.add(new_task)
    db.session.commit()

    task = data.Task.query.filter_by(name="Task for Only Office ID Pull").first()
    office1.tasks.append(task)
    office2.tasks.append(task)
    db.session.commit()
    task_id = task.id
    office_id = office1.id

    url='/pull_next_ticket'

    payload = {
        'task_id': None,

    }

    payload['ofc_id'] = office_id

    #create few tickets in both offices in interleaved manner
    import datetime
    now = datetime.datetime.utcnow()
    ticket_names = []
    for i in range(2):
        ticket1,exception1 = data.Serial.create_new_ticket(office=office1,task=task,name_or_number=f"OnlyOfficeIDTicket_O1_{i+1}")
        ticket2,exception2 = data.Serial.create_new_ticket(office=office2,task=task,name_or_number=f"OnlyOfficeIDTicket_O2_{i+1}")
        ticket_names.append(ticket1.name)
        if not exception1:
            ticket1.timestamp = now + datetime.timedelta(minutes=i*2)
            db.session.commit()
        if not exception2:
            ticket2.timestamp = now + datetime.timedelta(minutes=i*2 + 1)
            db.session.commit()
    # confirm tickets are created
    all_tickets_office1 = data.Serial.query.filter_by(office_id=office1.id, task_id=task.id).all()
    all_tickets_office2 = data.Serial.query.filter_by(office_id=office2.id, task_id=task.id).all()
    assert len(all_tickets_office1) == 2
    assert len(all_tickets_office2) == 2

    # now pull next ticket with only office id
    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    assert json_response['status'] == 'success'
    assert json_response['message'] == f'Ticket {ticket_names[0]} pulled successfully'
    assert json_response['ticket_name'] == ticket_names[0]

    #pull again to get second ticket
    resp = c.post(url,json=payload)
    assert resp.status_code == 200
    json_response = resp.get_json()
    assert json_response['status'] == 'success'
    assert json_response['message'] == f'Ticket {ticket_names[1]} pulled successfully'
    assert json_response['ticket_name'] == ticket_names[1]

