import pytest
from app.middleware import db
import app.database as data
from flask_wtf.csrf import generate_csrf



@pytest.mark.usefixtures("c")
def test_add_task_unauthorized(c,monkeypatch):
    class User:
        def __init__(self):
            self.role_id = 2  # non-admin role
    current_user = User()
    monkeypatch.setattr('app.views.tasks.current_user',current_user)

    office = data.Office(name="Test Office")
    db.session.add(office)
    db.session.commit()

    resp = c.post(f"/add_task/{office.id}", data={
        'name': 'Test Task',
        'hidden': False
    })
    assert resp.status_code == 403
    data_json = resp.get_json()
    assert data_json['status'] == 'error'
    assert data_json['message'] == 'Unauthorized access'


@pytest.mark.usefixtures("flask_app","c")
def test_add_task_form_validation_failure_missing_csrf(flask_app,c,monkeypatch):
    class User:
        def __init__(self):
            self.role_id = 1  # admin role
    current_user = User()
    monkeypatch.setattr('app.views.tasks.current_user',current_user)

    office = data.Office(name="Test Office")
    db.session.add(office)
    db.session.commit()

    #enable CSRF protection in the app for this test
    flask_app.config['WTF_CSRF_ENABLED'] = True


    resp = c.post(f"/add_task/{office.id}", data={
        'name': 'Task 1',
        'hidden': False
    })
    assert resp.status_code == 200
    data_json = resp.get_json()
    assert data_json['status'] == 'error'
    assert data_json['message'] == 'Form validation failed'


@pytest.mark.usefixtures("flask_app","c")
def test_add_task_duplicate_name_failure(flask_app,c,monkeypatch):
    class User:
        def __init__(self):
            self.role_id = 1  # admin role
    current_user = User()
    monkeypatch.setattr('app.views.tasks.current_user',current_user)


    #enable CSRF protection in the app for this test
    flask_app.config['WTF_CSRF_ENABLED'] = True

    #Initial GET to set up session
    c.get('/')
    with flask_app.test_request_context():
        csrf_token = generate_csrf()

    unrelated_office = data.Office(name="Unrelated test Office")
    db.session.add(unrelated_office)
    db.session.commit()
    unrelated_office_id = unrelated_office.id

    office = data.Office(name="Test Office")
    db.session.add(office)
    db.session.commit()
    office_id = office.id

    task_name = 'Task 1'

    # unrelated office's task 
    unrelated_office_task = data.Task(task_name, False)
    db.session.add(unrelated_office_task)
    db.session.commit()

    # Add initial task
    task = data.Task(task_name, False)
    db.session.add(task)
    db.session.commit()

    #attach both tasks to their respective offices
    office.tasks.append(task)
    unrelated_office.tasks.append(unrelated_office_task)
    db.session.commit()

    new_name = ' Task 1 '  # Duplicate name with whitespace difference to test stripping too

    
    resp = c.post(f"/add_task/{office_id}", data={
        'name': new_name,
        'hidden': False,
        'csrf_token': csrf_token
    })
    assert resp.status_code == 200
    data_json = resp.get_json()
    assert data_json['status'] == 'error'
    assert data_json['message'] == 'Task with this name already exists in this office'




@pytest.mark.usefixtures("flask_app","c")
def test_add_task_success_different_offices_same_task(flask_app,c,monkeypatch):
    """
    task already exists in another office but not in this one
    so it should be added successfully
    """
    class User:
        def __init__(self):
            self.role_id = 1  # admin role
    current_user = User()
    monkeypatch.setattr('app.views.tasks.current_user',current_user)

    #enable CSRF protection in the app for this test
    flask_app.config['WTF_CSRF_ENABLED'] = True

    #Initial GET to set up session
    c.get('/')

    with flask_app.test_request_context():
        csrf_token = generate_csrf()
    office1 = data.Office(name="Office 1")
    office2 = data.Office(name="Office 2")

    db.session.add(office1)
    db.session.add(office2)
    db.session.commit()

    # enter a task directly in database and attach to office1
    task = data.Task('Task 1', False)
    db.session.add(task)
    db.session.commit()
    office1.tasks.append(task)
    db.session.commit()

    # now try to add the same task to office2
    resp = c.post(f"/add_task/{office2.id}", data={
        'name': 'Task 1',
        'hidden': False,
        'csrf_token': csrf_token
    })
    assert resp.status_code == 200 
    data_json = resp.get_json()
    assert data_json['status'] == 'success'
    assert data_json['message'] == 'Task added successfully'



@pytest.mark.usefixtures("flask_app","c")
def test_add_task_success_new_task_in_entire_database(flask_app,c,monkeypatch):
    """
    first task in database
    """
    
    class User:
        def __init__(self):
            self.role_id = 1  # admin role
    current_user = User()
    monkeypatch.setattr('app.views.tasks.current_user',current_user)


    #enable CSRF protection in the app for this test
    flask_app.config['WTF_CSRF_ENABLED'] = True

   
    import app.database as data


    #Initial GET to set up session
    c.get('/')
    with flask_app.test_request_context():
        csrf_token = generate_csrf()

    office = data.Office(name="Test Office")
    db.session.add(office)
    db.session.commit()
    office_id = office.id

    
    resp = c.post(f"/add_task/{office.id}", data={
        'name': 'Task 1',
        'hidden': False,
        'csrf_token': csrf_token
    })
    assert resp.status_code == 200
    data_json = resp.get_json()
    assert data_json['status'] == 'success'
    assert data_json['message'] == 'Task added successfully'

    # Verify that the task was added to the database
    task_in_db = data.Task.query.filter_by(name='Task 1').first()
    assert task_in_db is not None

    #fetch office again
    office = data.Office.query.get(office_id)
    
    #assert task in office 
    assert task_in_db in office.tasks