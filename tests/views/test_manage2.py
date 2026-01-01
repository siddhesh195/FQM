import pytest
import app.database as database

from app.middleware import db

@pytest.mark.usefixtures('c')
def test_manage_home(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    response = c.get('/manage_home')
    assert response.status_code == 200
    assert b'Management Home' in response.data


@pytest.mark.usefixtures('c')
def test_get_all_tasks_not_authorized(c, monkeypatch):
    class user:
        role_id = 2  # Not an admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    response = c.get('/get_all_tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Unauthorized'


@pytest.mark.usefixtures('c')
def test_get_all_tasks_success(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    # get all existing tasks from the database
    existing_tasks = database.Task.query.all()

    response = c.get('/get_all_tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'tasks' in data
    assert len(data['tasks']) == len(existing_tasks)



@pytest.mark.usefixtures('c')
def test_modify_task_not_authorized(c,monkeypatch):
    class user:
        role_id = 2  # Not an admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)
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
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

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
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

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
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

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
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

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
def test_modify_task_name_change_success(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

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

@pytest.mark.usefixtures('c')
def test_get_all_offices_not_authorized(c, monkeypatch):
    class user:
        role_id = 2  # Not an admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    response = c.get('/get_all_offices')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Unauthorized'



@pytest.mark.usefixtures('c')
def test_get_all_offices_success(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    # get all existing offices from the database
    existing_offices = database.Office.query.all()
    assert len(existing_offices) > 0  # Ensure there are offices in the database

    response = c.get('/get_all_offices')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'offices' in data
    assert len(data['offices']) == len(existing_offices)

@pytest.mark.usefixtures('c')
def test_get_all_offices_some_with_tasks(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    # Ensure there is at least one office with tasks and one without
    office_with_tasks = database.Office(name='Office With Tasks')
    office_without_tasks = database.Office(name='Office Without Tasks')
    db.session.add(office_with_tasks)
    db.session.add(office_without_tasks)
    db.session.commit()

    task1 = database.Task(name='Task 1', hidden=False)
    task2 = database.Task(name='Task 2', hidden=False)
    db.session.add(task1)
    db.session.add(task2)
    db.session.commit()

    # Associate tasks with the office
    office_with_tasks.tasks.append(task1)
    office_with_tasks.tasks.append(task2)
    db.session.commit()

    response = c.get('/get_all_offices')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'offices' in data

    offices_dict = {office['name']: office for office in data['offices']}
    assert 'Office With Tasks' in offices_dict
    assert 'Office Without Tasks' in offices_dict

    assert len(offices_dict['Office With Tasks']['tasks']) == 2
    assert len(offices_dict['Office Without Tasks']['tasks']) == 0


@pytest.mark.usefixtures('c')
def test_modify_office_not_authorized(c,monkeypatch):
    class user:
        role_id = 2  # Not an admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)
    new_office = database.Office(name='Test Office')

    db.session.add(new_office)
    db.session.commit()
    new_office = database.Office.query.filter_by(name='Test Office').first()
    assert new_office.name == 'Test Office'

    response = c.post('/modify_office', json={'office_id': 1, 'officeName': 'Updated Office'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Unauthorized'

@pytest.mark.usefixtures('c')
def test_modify_office_not_found(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    # add a new Office
    new_office = database.Office(name='Test Office')
    db.session.add(new_office)
    db.session.commit()

    new_office = database.Office.query.filter_by(name='Test Office').first()
    assert new_office.name == 'Test Office'

    non_existent_office_name = "Non-existent Office"
    non_existent_office = database.Office.query.filter_by(name=non_existent_office_name).first()

    assert non_existent_office is None

    non_existent_office_id = 9999  # Assuming this ID does not exist
    response = c.post(f'/modify_office', json={'office_id': non_existent_office_id, 'officeName': 'Updated Name'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Office not found'

@pytest.mark.usefixtures('c')
def test_modify_office_no_office_id(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    response = c.post('/modify_office', json={'officeName': 'Updated Name'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Office ID not provided'

@pytest.mark.usefixtures('c')
def test_modify_office_name_change_success(c, monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.manage2.current_user', current_user)

    # add a new Office
    new_office = database.Office(name='Original Office Name')

    db.session.add(new_office)
    db.session.commit()

    #assert the office has the original name
    office = database.Office.query.get(new_office.id)
    assert office.name == 'Original Office Name'

    response = c.post('/modify_office', json={'office_id': new_office.id, 'officeName': 'Updated Office Name'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == f'Office {new_office.name} updated successfully'
    # Verify that the office name is now updated
    office = database.Office.query.get(new_office.id)
    assert office.name == 'Updated Office Name'
