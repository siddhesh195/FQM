import pytest
import app.database as database
from app.middleware import db




@pytest.mark.usefixtures('flask_app','c')
def test_cannot_modify_office_with_active_tickets(flask_app,c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    # add a new Office
    new_office = database.Office(name='Office With Tickets')
    db.session.add(new_office)
    db.session.commit()

    # add a new Task
    new_task = database.Task(name='Task For Office With Tickets', hidden=False)
    db.session.add(new_task)
    db.session.commit()

    # Associate task with the office
    new_office.tasks.append(new_task)
    db.session.commit()

    # Add an active ticket for the office
    office = database.Office.query.get(new_office.id)
    task = database.Task.query.get(new_task.id)
    
    new_ticket, exception = database.Serial.create_new_ticket(office=office, task=task,name_or_number='Test Ticket')
    db.session.add(new_ticket)
    db.session.commit()

    response = c.post('/modify_office', json={'office_id': new_office.id, 'taskId': new_task.id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Cannot remove tasks from office with active tickets'

    response2 = c.post('/modify_office', json={'office_id': new_office.id, 'officeName': 'New Name'})
    assert response2.status_code == 200
    data2 = response2.get_json()
    assert data2['status'] == 'error'
    assert data2['message'] == 'Cannot rename office with active tickets'