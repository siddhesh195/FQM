import pytest
import app.database as database
from app.middleware import db
from flask_wtf.csrf import generate_csrf

def get_csrf_token(c, flask_app):

    flask_app.config["WTF_CSRF_ENABLED"] = True
    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with flask_app.test_request_context():
        token = generate_csrf()
    return token


@pytest.mark.usefixtures("flask_app",'c')
def test_add_common_task_successful(flask_app,c,monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    

    token = get_csrf_token(c, flask_app)

    # Ensure there are offices in the database
    office1 = database.Office(name='Office 1')
    office2 = database.Office(name='Office 2')
    db.session.add(office1)
    db.session.add(office2)
    db.session.commit()
   
 
    # Prepare form data
    form_data = {
        'name': 'New Common Task',
        f'check{office1.id}': True,
        f'check{office2.id}': True,
        'csrf_token': token
    }   

    response = c.post('/add_common_task', data=form_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == 'Common task added successfully'

    # Verify that the task was created in the database
    task = database.Task.query.filter_by(name='New Common Task').first()
    assert task is not None
    assert task.name == 'New Common Task'
    assert task.hidden == False
    task_office_ids = [office.id for office in task.offices]
    assert office1.id in task_office_ids
    assert office2.id in task_office_ids

    #now change hidden status to True and test again

    form_data = {
            'name': 'New Common Task Hidden',
            'hidden': True, # can be anything that is considered truthy
            f'check{office1.id}': True,
            f'check{office2.id}': True,
            'csrf_token': token
        }
    response = c.post('/add_common_task', data=form_data)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['message'] == 'Common task added successfully'
    # Verify that the task was created in the database
    task = database.Task.query.filter_by(name='New Common Task Hidden').first()
    assert task is not None
    assert task.name == 'New Common Task Hidden'
    assert task.hidden == True
    task_office_ids = [office.id for office in task.offices]
    assert office1.id in task_office_ids
    assert office2.id in task_office_ids
    
    
@pytest.mark.usefixtures("flask_app",'c')
def test_add_common_task_unauthorized(flask_app,c,monkeypatch):
    class user:
        role_id = 2  # Not an admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    token = get_csrf_token(c, flask_app)

    response = c.post('/add_common_task', data={
        'name': 'Unauthorized Task',
        'csrf_token': token
    })
    assert response.status_code == 403
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Unauthorized access'


@pytest.mark.usefixtures("flask_app",'c')
def test_add_common_task_no_office_selected(flask_app,c,monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    token = get_csrf_token(c, flask_app)

    response = c.post('/add_common_task', data={
        'name': 'Task Without Office',
        'csrf_token': token
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'At least one office must be selected'


@pytest.mark.usefixtures("flask_app",'c')
def test_add_common_task_form_validation_failed(flask_app,c,monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    token = get_csrf_token(c, flask_app)

    response = c.post('/add_common_task', data={
        # Missing 'name' field
        'csrf_token': token
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Form validation failed'


@pytest.mark.usefixtures("flask_app",'c')
def test_add_common_task_duplicate_name(flask_app,c,monkeypatch):
    class user:
        role_id = 1  # Admin
    current_user = user()
    monkeypatch.setattr('app.views.tasks.current_user', current_user)

    task_name='Existing Task'

    # Create an existing task
    existing_task = database.Task(name=task_name, hidden=False)
    db.session.add(existing_task)
    db.session.commit()

    # Ensure there is an office in the database
    office = database.Office(name='Office 1')
    office_id = office.id
    db.session.add(office)
    db.session.commit()

    token = get_csrf_token(c, flask_app)

    new_task_name =  " " +task_name + " " # Same name as existing task with extra spaces to test stripping

    response = c.post('/add_common_task', data={
        'name': new_task_name,
        f'check{office_id}': True,
        'csrf_token': token
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['message'] == 'Task name is already in use'


