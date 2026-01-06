import pytest
import app.database as database
from app.middleware import db

# TO:DO enable csrf protection in tests later and change tests accordingly





@pytest.mark.usefixtures('c')
def test_modify_task_not_authorized(c,monkeypatch):
    class user:
        role_id = 2  # Not an admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)
    new_task = database.Task(name='Test Task', hidden=True)

    db.session.add(new_task)
    db.session.commit()
    new_task = database.Task.query.filter_by(name='Test Task').first()
    assert new_task.hidden == True

    response = c.post('/modify_task', json={'task_id': 1, 'status': False})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Unauthorized'


@pytest.mark.usefixtures('c')
def test_modify_task_not_found(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    # add a new Task
    new_task = database.Task(name='Test Task', hidden=True)
    db.session.add(new_task)
    db.session.commit()

    new_task = database.Task.query.filter_by(name='Test Task').first()
    assert new_task.hidden == True

    non_existent_task_name = "Non-existent Task"
    non_existent_task = database.Task.query.filter_by(name=non_existent_task_name).first()

    assert non_existent_task is None

    non_existent_task_id = 9999  # Assuming this ID does not exist
    response = c.post(f'/modify_task', json={'task_id': non_existent_task_id, 'status': False})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Task not found'


@pytest.mark.usefixtures('c')
def test_modify_task_no_task_id(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    response = c.post('/modify_task', json={'status': False})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Task ID not provided'


@pytest.mark.usefixtures('c')
def test_modify_task_task_unhide_success(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    # add a new Task
    new_task = database.Task(name='Test Task to Unhide', hidden=True)

    db.session.add(new_task)
    db.session.commit()

    #assert the task is hidden
    task = database.Task.query.get(new_task.id)
    assert task.hidden == True

    response = c.post('/modify_task', json={'task_id': new_task.id, 'status': False})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == f'Task {new_task.name} status updated to False'
    # Verify that the task is now unhidden
    task = database.Task.query.get(new_task.id)
    assert task.hidden == False


@pytest.mark.usefixtures('c')
def test_modify_task_task_hide_success(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    # add a new Task
    new_task = database.Task(name='Test Task to Unhide', hidden=False)

    db.session.add(new_task)
    db.session.commit()

    #assert the task is hidden
    task = database.Task.query.get(new_task.id)
    assert task.hidden == False

    response = c.post('/modify_task', json={'task_id': new_task.id, 'status': True})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == f'Task {new_task.name} status updated to True'
    # Verify that the task is now unhidden
    task = database.Task.query.get(new_task.id)
    assert task.hidden == True


@pytest.mark.usefixtures('c')
def test_modify_task_name_change_duplicate_failure(c, monkeypatch):
    """
    modify a task name to a name that already exists in the same office should fail
    """
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    # add a new Task
    new_task = database.Task(name='Existing Task Name', hidden=False)
    new_task_name= new_task.name
    db.session.add(new_task)
    db.session.commit()

    # add a new office
    new_office = database.Office(name='Test Office')
    db.session.add(new_office)
    db.session.commit()
    # associate the task with the office
    new_task.offices.append(new_office)
    db.session.commit()
    # add another task with different name to same office
    another_task = database.Task(name='Another Task Name', hidden=False)
    db.session.add(another_task)
    db.session.commit()
    another_task.offices.append(new_office)
    db.session.commit()
    #attempt to change another_task's name to existing task name
    
    #add whitespaces to test strip
    new_task_name= "   "+ new_task_name + "   "

    response = c.post('/modify_task', json={'task_id': another_task.id, 'taskName': new_task_name})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Task with this name already exists in this office'


@pytest.mark.usefixtures('c')
def test_modify_task_name_change_duplicate_success_different_offices(c, monkeypatch):
    """
    modify a task name to a name that already exists in the same office should fail
    """
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    # add a new Task
    new_task = database.Task(name='Existing Task Name', hidden=False)
    db.session.add(new_task)
    db.session.commit()

    # add a new office
    new_office = database.Office(name='Test Office')
    db.session.add(new_office)
    db.session.commit()
    # associate the task with the office
    new_task.offices.append(new_office)
    db.session.commit()
    # add another office
    another_office = database.Office(name='Another Test Office')
    db.session.add(another_office)
    db.session.commit()

    # add another task with different name to different office
    another_task = database.Task(name='Another Task Name', hidden=False)
    db.session.add(another_task)
    db.session.commit()
    another_task.offices.append(another_office)
    db.session.commit()

    #attempt to change another_task's name to existing task name
    # This should succeed as they are in different offices
    

    response = c.post('/modify_task', json={'task_id': another_task.id, 'taskName': new_task.name})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == f'Task {new_task.name} status updated to None'


@pytest.mark.usefixtures('c')
def test_modify_task_name_change_success(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    # add a new Task
    new_task = database.Task(name='Original Task Name', hidden=False)

    db.session.add(new_task)
    db.session.commit()

    #assert the task has the original name
    task = database.Task.query.get(new_task.id)
    assert task.name == 'Original Task Name'

    response = c.post('/modify_task', json={'task_id': new_task.id, 'taskName': 'Updated Task Name'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == f'Task Updated Task Name status updated to None'
    # Verify that the task name is now updated
    task = database.Task.query.get(new_task.id)
    assert task.name == 'Updated Task Name'