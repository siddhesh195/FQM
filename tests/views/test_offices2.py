import pytest
import app.database as data
from app.helpers import has_offices
from tests.__init__ import fill_tickets,fill_offices


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
def test_delete_all_offices_unauthorized_access(c, monkeypatch):
    """
    Test deleting all offices when user is not admin.
    """
    class user:
        def __init__(self):
            self.role_id = 2
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user)
    response = c.post("/delete_all_offices")
    assert response.status_code == 403
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "Unauthorized access"

@pytest.mark.usefixtures("c")
def test_delete_all_offices__failure_offices_not_empty(c, monkeypatch):
    """
    Test deleting all offices when offices are not empty.
    """
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user)
    monkeypatch.setattr("app.views.offices.has_offices", lambda: True)
    response = c.post("/delete_all_offices")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "Cannot delete offices with existing tickets. Please reset all offices first."
@pytest.mark.usefixtures("c")
def test_delete_all_offices_failure_no_offices(c, monkeypatch):
    """
    Test deleting all offices when there are no offices.
    """
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user)
    monkeypatch.setattr("app.views.offices.has_offices", lambda: False)
    response = c.post("/delete_all_offices")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "error"
    assert data_response["message"] == "No offices to delete"

@pytest.mark.usefixtures("c")
def test_delete_all_offices_success(c, monkeypatch):
    """
    Test successful deletion of all offices.
    """
    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr("app.views.offices.current_user", current_user)
    monkeypatch.setattr("app.views.offices.has_offices", lambda: True)

    #reset all offices first
    tickets = data.Serial.query.filter(data.Serial.number != 100)
    tickets_count_before_deletion = tickets.count()
    
    response = c.post("/reset_all_offices")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "success"
    assert data_response["message"] == "All offices have been reset"

    offices = data.Office.query.all()
    offices_count_before_deletion = len(offices)  
    assert offices_count_before_deletion > 0
     

    #then delete all offices
    response = c.post("/delete_all_offices")
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response["status"] == "success"
    assert data_response["message"] == "All offices have been deleted"

    #sanity check to ensure offices are deleted
    offices_after_deletion = data.Office.query.all()
    assert len(offices_after_deletion) == 0
    

    #restore data
    fill_offices()
    fill_tickets()
    tickets2 = data.Serial.query.filter(data.Serial.number != 100)
    assert tickets2.count() == tickets_count_before_deletion

    offices = data.Office.query.all()
    assert len(offices) == offices_count_before_deletion



    

