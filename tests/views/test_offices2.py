import pytest
import app.database as data


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