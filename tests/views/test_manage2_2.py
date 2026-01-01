import pytest
from app.middleware import db
from flask import url_for
import app.database as database



@pytest.mark.usefixtures('c')
def test_delete_task_unauthorized(c,monkeypatch):
    class user:
        role_id = 2  # Not an admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    response = c.post('/delete_a_task', json={'task_id': 1})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Unauthorized'

@pytest.mark.usefixtures('c')
def test_delete_task_id_not_provided(c,monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)
    response = c.post('/delete_a_task', json={})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Task ID not provided'

@pytest.mark.usefixtures('c')
def test_delete_task_not_found(c,monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)
    response = c.post('/delete_a_task', json={'task_id': 9999})  # Assuming this ID does not exist
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Task not found'


@pytest.mark.usefixtures('c')
def test_delete_task_no_office_success(c,monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    # First, create a task to delete

    new_task = database.Task(name='Test Task for Deletion', hidden=False)
    db.session.add(new_task)
    db.session.commit()
    task_id = new_task.id

    response = c.post('/delete_a_task', json={'task_id': task_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == f'Task {new_task.name} deleted successfully'

    # Verify the task is actually deleted
    deleted_task = database.Task.query.get(task_id)
    assert deleted_task is None

@pytest.mark.usefixtures('c')
def test_delete_task_with_office_success(c,monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    # First, create an office and a task associated with it
    new_office = database.Office(name='Test Office')
    db.session.add(new_office)
    db.session.commit()

    new_task = database.Task(name='Test Task with Office', hidden=False)
    db.session.add(new_task)
    db.session.commit()
    task_id = new_task.id

    # Associate task with office
    new_office.tasks.append(new_task)
    db.session.commit()

    office_task = new_office.tasks[0]
    assert office_task.id == task_id  # Ensure association is correct

    response = c.post('/delete_a_task', json={'task_id': task_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == f'Task {new_task.name} deleted successfully'

    # Verify the task is actually deleted
    deleted_task = database.Task.query.get(task_id)
    assert deleted_task is None