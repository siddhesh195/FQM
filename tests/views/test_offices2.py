import pytest
import app.database as data
from app.helpers import has_offices
from tests.__init__ import fill_tickets,fill_offices,fill_tasks



@pytest.mark.usefixtures("c")
def test_fetch_office_and_task_ids(c):
    
    all_offices = data.Office.query.all()
    all_tasks = data.Task.query.all()

    for office in all_offices:
        print(f"Office ID: {office.id}, Name: {office.name}")

    for task in all_tasks:
        print(f"Task ID: {task.id}, Name: {task.name}")

    response = c.get("/fetch_office_and_task_ids")

    assert response.status_code == 200
    data_response = response.get_json()
    assert "office_ids" in data_response
    assert "task_ids" in data_response
    
    fetched_office_ids = data_response["office_ids"]
    fetched_task_ids = data_response["task_ids"]

    expected_office_ids = [office.id for office in all_offices]
    expected_task_ids = [task.id for task in all_tasks]

    assert set(fetched_office_ids) == set(expected_office_ids)
    assert set(fetched_task_ids) == set(expected_task_ids)

@pytest.mark.usefixtures("c")
def test_reset_all_offices_success(c,monkeypatch):
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    assert has_offices() == True
    monkeypatch.setattr("app.views.offices.current_user", current_user) 

    tickets = data.Serial.query.filter(data.Serial.number != 100)
    assert tickets.count() > 0
    initial_tickets_count = tickets.count()
    response = c.post("/reset_all_offices")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "success"
    tickets2 = data.Serial.query.filter(data.Serial.number != 100)
    assert tickets2.count() == 0

    #restore data
    fill_tickets()
    tickets3 = data.Serial.query.filter(data.Serial.number != 100)
    assert tickets3.count() == initial_tickets_count

@pytest.mark.usefixtures("c")
def test_reset_all_offices_unauthorized(c,monkeypatch):
    class user:
        def __init__(self):
            self.role_id = 2
    current_user = user()
    assert has_offices() == True
    monkeypatch.setattr("app.views.offices.current_user", current_user) 

    response = c.post("/reset_all_offices")
    assert response.status_code == 403
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "Unauthorized access"

@pytest.mark.usefixtures("c")
def test_reset_all_offices_no_offices(c,monkeypatch):
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user) 
    monkeypatch.setattr("app.views.offices.has_offices", lambda: False)

    response = c.post("/reset_all_offices")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "No offices to reset"

@pytest.mark.usefixtures("c")
def test_reset_all_offices_error(c,monkeypatch):
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    assert has_offices() == True
    monkeypatch.setattr("app.views.offices.current_user", current_user) 
    def raise_exception():
        raise Exception("Database error")
    monkeypatch.setattr("app.views.offices.data.db.session.commit", raise_exception)

    response = c.post("/reset_all_offices")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "An error occurred while resetting offices"

@pytest.mark.usefixtures("c")
def test_delete_all_offices_and_tasks_unauthorized_access(c, monkeypatch):
    """
    Test deleting all offices when user is not admin.
    """
    class user:
        def __init__(self):
            self.role_id = 2
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user)
    response = c.post("/delete_all_offices_and_tasks")
    assert response.status_code == 403
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "Unauthorized access"

@pytest.mark.usefixtures("c")
def test_delete_all_offices_and_tasks_failure_offices_not_empty(c, monkeypatch):
    """
    Test deleting all offices and tasks when offices are not empty.
    """
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user)
    monkeypatch.setattr("app.views.offices.has_offices", lambda: True)
    response = c.post("/delete_all_offices_and_tasks")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "Cannot delete offices with existing tickets. Please reset all offices first."
@pytest.mark.usefixtures("c")
def test_delete_all_offices_and_tasks_failure_no_offices(c, monkeypatch):
    """
    Test deleting all offices and tasks when there are no offices.
    """
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user)
    monkeypatch.setattr("app.views.offices.has_offices", lambda: False)
    response = c.post("/delete_all_offices_and_tasks")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "No offices to delete"

@pytest.mark.usefixtures("c")
def test_delete_all_offices_and_tasks_success(c, monkeypatch):
    """
    Test successful deletion of all offices and tasks.
    """
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user)
    monkeypatch.setattr("app.views.offices.has_offices", lambda: True)

    #get all tasks
    tasks = data.Task.query.all()
    tasks_count_before_deletion = len(tasks)
    assert tasks_count_before_deletion > 0

    #reset all offices first
    tickets = data.Serial.query.filter(data.Serial.number != 100)
    tickets_count_before_deletion = tickets.count()
    assert tickets_count_before_deletion > 0
    
    response = c.post("/reset_all_offices")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "success"
    assert data_response["message"] == "All offices have been reset"

    offices = data.Office.query.all()
    offices_count_before_deletion = len(offices)  
    assert offices_count_before_deletion > 0

    tasks = data.Task.query.all()
    assert len(tasks) > 0
    tasks_count_before_deletion = len(tasks)

    #create a new office
    office = data.Office(name="TempOffice", prefix="TO")
    data.db.session.add(office)
    data.db.session.commit()
    assert data.Office.query.filter_by(name="TempOffice", prefix="TO").first() is not None

    #create a new user
    user = data.User(name="TempUser", password="TempPass", role_id=1)
    data.db.session.add(user)
    data.db.session.commit()
    assert data.User.query.filter_by(name="TempUser").first() is not None

    #make the user new office's operator
    operator = data.Operators(id=user.id, office_id=office.id)
    data.db.session.add(operator)
    data.db.session.commit()
    new_operator = data.Operators.query.filter_by(id=user.id, office_id=office.id).first()
    assert new_operator is not None
     

    #then delete all offices
    response = c.post("/delete_all_offices_and_tasks")
    assert response.status_code == 200
    data_response = response.get_json()
    print(data_response)
    assert data_response["status"] == "success"
    assert data_response["message"] == "All offices have been deleted"

    #sanity check to ensure offices and tasks are deleted
    offices_after_deletion = data.Office.query.all()
    assert len(offices_after_deletion) == 0
    
    tasks_after_deletion = data.Task.query.all()
    assert len(tasks_after_deletion) == 0

   

    tasks = data.Task.query.all()
    assert len(tasks) == tasks_count_before_deletion




