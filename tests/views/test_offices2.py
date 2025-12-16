import pytest
import app.database as data
from app.helpers import has_offices
from tests.__init__ import fill_tickets


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
def test_reset_all_offices(c,monkeypatch):
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
    fill_tickets()
    tickets3 = data.Serial.query.filter(data.Serial.number != 100)
    assert tickets3.count() == initial_tickets_count
    

