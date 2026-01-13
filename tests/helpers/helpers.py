
from app import database


def add_and_assert_office(office_name, office_prefix, client):
    """Helper function to add an office and assert success."""
    office_data = {
        'name': office_name,
        'prefix': office_prefix
    }
    add_office_url= '/add_office'

    response = client.post(add_office_url, json=office_data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'Office added successfully' in response.json['message']
    office = database.Office.query.filter_by(name=office_name).first()
    assert office is not None
    return office

def add_and_assert_common_task(task_name, office_ids, client):
    """Helper function to add a common task and assert success."""
    task_data = {
        'name': task_name,
    }
    for office_id in office_ids:
        task_data[f'check{office_id}'] = True

    add_task_url= '/add_common_task'

    response = client.post(add_task_url, json=task_data)
    print(response.json)
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'Common task added successfully' in response.json['message']
    task = database.Task.query.filter_by(name=task_name).first()
    assert task is not None
    return task

def add_and_assert_task(task_name, office_id, client):
    """Helper function to add a task to an office and assert success."""
    task_data = {
        'name': task_name,
        'hidden': False
    }
    add_task_url= f'/add_task/{office_id}'

    response = client.post(add_task_url, json=task_data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'Task added successfully' in response.json['message']
    task = database.Task.query.filter_by(name=task_name).first()
    assert task is not None
    return task