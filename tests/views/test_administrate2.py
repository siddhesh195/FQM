import pytest
import app.database as data
from app.middleware import db
from werkzeug.security import check_password_hash
from flask_wtf.csrf import generate_csrf


def add_user(name, password, role_id):
    user = data.User(name, password, role_id)
    db.session.add(user)
    db.session.commit()
    return user

def add_office(name, prefix):
    office = data.Office(name, prefix)
    db.session.add(office)
    db.session.commit()
    return office

def monkeypatch_current_user(monkeypatch, role_id=2):
    class User:
        def __init__(self):
            self.role_id = role_id  # Non-admin role
    
    user = User()
    monkeypatch.setattr('app.views.administrate2.current_user', user)

def make_user_operator(user_id, office_id):
    operator = data.Operators(user_id, office_id)
    db.session.add(operator)
    db.session.commit()
    return operator

def assert_same_password(password_hash, plain_password):
    assert check_password_hash(password_hash, plain_password)

def get_csrf_token(c, flask_app):

    flask_app.config["WTF_CSRF_ENABLED"] = True
    #Initial GET to set up session
    c.get('/')

    #Get correct CSRF token from session:
    with flask_app.test_request_context():
        token = generate_csrf()
    return token

@pytest.mark.usefixtures('flask_app','c')
def test_update_user_unauthorized(flask_app, c, monkeypatch):
    
    monkeypatch_current_user(monkeypatch, role_id=2)  # Non-admin role
    token = get_csrf_token(c, flask_app)
    
    response = c.post('/update_user/1', data={
        'name': 'new_name',
        'password': 'new_pass',
        'role': 2,
        'csrf_token': token
    })

    assert response.status_code == 403
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Unauthorized access'
   


@pytest.mark.usefixtures('flask_app','c')
def test_update_user_not_found(flask_app, c, monkeypatch):
    
    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    token = get_csrf_token(c, flask_app)
    
    response = c.post('/update_user/9999', data={
        'name': 'new_name',
        'password': 'new_pass',
        'role': 2,
        'csrf_token': token
    })

    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'User not found'
    


@pytest.mark.usefixtures('flask_app','c')
def test_update_user_duplicate_name(flask_app, c, monkeypatch):

    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    token = get_csrf_token(c, flask_app)
    
    #add two users first
    user1 = add_user('existing_user', 'pass1', 2)
    user2 = add_user('user_to_update', 'pass2', 2)

    response = c.post(f'/update_user/{user2.id}', data={
        'name': 'existing_user',  # Duplicate name
        'password': 'new_pass',
        'role': 2,
        'csrf_token': token
    })

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'User name already exists'
    


@pytest.mark.usefixtures('flask_app','c')
def test_update_user_too_short(flask_app, c, monkeypatch):
    """
    Test case where password and user name is too short"""

    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    
    #add a user first
    user_name = 'user_to_update'
    user_password = 'initial_pass'
    user_role = 2

    
    token = get_csrf_token(c, flask_app)
    user = add_user(user_name, user_password, user_role)

    response = c.post(f'/update_user/{user.id}', data={
        'name': 'new_name',
        'password': 'shrt',  # Too short password
        'role': user_role,
        'csrf_token': token
    })

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Invalid form data'

    response = c.post(f'/update_user/{user.id}', data={
        'name': 'shrt',  # Too short name
        'password': 'password',  # Too short password
        'role': user_role
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Invalid form data'

@pytest.mark.usefixtures('flask_app','c')
def test_form_validation_failure(flask_app, c, monkeypatch):
    """
    Test case where form validation fails
    """
    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    
    #add a user first
    user_name = 'user_to_update'
    user_password = 'initial_pass'
    user_role = 2

    
    token = get_csrf_token(c, flask_app)
    user = add_user(user_name, user_password, user_role)

    response = c.post(f'/update_user/{user.id}', data={
        'name': 'f',  # Name with less than 5 letters
        'password': 'new_pass',
        'role': user_role,
        'csrf_token': token
    })

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'Invalid form data'

@pytest.mark.usefixtures('flask_app','c')
def test_update_user_whitespace_name(flask_app, c, monkeypatch):
    """
    Test case where name is only whitespace
    """
    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    
    #add a user first
    user_name = 'user_to_update'
    user_password = 'initial_pass'
    user_role = 2

    
    token = get_csrf_token(c, flask_app)
    user = add_user(user_name, user_password, user_role)

    response = c.post(f'/update_user/{user.id}', data={
        'name': '     ',  # Name with only whitespace
        'password': 'new_pass',
        'role': user_role,
        'csrf_token': token
    })

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert json_data['message'] == 'You entered empty name'

@pytest.mark.usefixtures('flask_app','c')
def test_update_user_success_name_change(flask_app, c, monkeypatch):
    """
    Existing user is an operator, change name successfully
    """
    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    
    #add a user first
    user_name = 'user_to_update'
    user_password = 'initial_pass'
    user_role = 3 #operator role

    token = get_csrf_token(c, flask_app)

    user = add_user(user_name, user_password, user_role)
    new_name = 'updated_user_name'
    
    response = c.post(f'/update_user/{user.id}', data={
        'name': new_name,
        'password': user_password,
        'csrf_token': token
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == 'User updated successfully'
    updated_user = data.User.get(user.id)
    assert updated_user.name == new_name
    assert_same_password(updated_user.password_hash, user_password)

@pytest.mark.usefixtures('flask_app','c')
def test_update_user_operator_name_change_success(flask_app, c, monkeypatch):
    """
    Existing user is operator, change name successfully
    """
    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    
    #add a user first
    user_name = 'user_to_update'
    user_password = 'initial_pass'
    user_role = 3 #operator role

    token = get_csrf_token(c, flask_app)

    user = add_user(user_name, user_password, user_role)
    new_name = 'updated_user_name'

    # create an office for the operator, we need a name and a prefix
    
    office = add_office('Office1', 'O')
    office_id = office.id

    #make the user an operator
    operator = make_user_operator(user.id, office_id)
    

    response = c.post(f'/update_user/{user.id}', data={
        'name': new_name,
        'password': user_password,
        'role': user_role,
        'offices': office_id,
        'csrf_token': token
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == 'User updated successfully'
    updated_user = data.User.get(user.id)
    password_hash = updated_user.password_hash
    assert_same_password(password_hash, user_password)


@pytest.mark.usefixtures('flask_app','c')
def test_update_user_success_make_operator(flask_app, c, monkeypatch):
    """
    Existing user is not an operator, update successfully by making user the operator
    """
    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    
    #add a user first
    user_name = 'user_to_update'
    user_password = 'initial_pass'
    user_role = 2 #non-operator role

    
    token = get_csrf_token(c, flask_app)

    user = add_user(user_name, user_password, user_role)
   
    #new_name = 'updated_user_name'
    new_role_id = 3  # Change to operator role

    

    response = c.post(f'/update_user/{user.id}', data={
        'name': user_name,
        'password': user_password,
        'role': new_role_id,
        'csrf_token': token
    })
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == 'User updated successfully'
    updated_user = data.User.get(user.id)
    assert updated_user.role_id == new_role_id
    assert_same_password(updated_user.password_hash, user_password)



@pytest.mark.usefixtures('flask_app','c')
def test_update_user_success_remove_operator(flask_app, c, monkeypatch):
    """
    Existing user is an operator, update successfully to non-operator
    """

    monkeypatch_current_user(monkeypatch, role_id=1)  # Admin role
    
    
    #add a user first
    user_name = 'user_to_update'
    user_password = 'initial_pass'
    user_role = 3 #operator role

    token = get_csrf_token(c, flask_app)

    user = add_user(user_name, user_password, user_role)
    new_role_id = 2  # Change to non-operator role

    # create an office for the operator, we need a name and a prefix
    office = add_office('Office1', 'O')
    office_id = office.id

    #make the user an operator
    operator = make_user_operator(user.id, office_id)
    

    response = c.post(f'/update_user/{user.id}', data={
        'name': user_name,
        'password': user_password,
        'role': new_role_id,
        'csrf_token': token
    })
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == 'User updated successfully'
    updated_user = data.User.get(user.id)
    assert updated_user.role_id == new_role_id
    #check operator removed
    operator_check = data.Operators.get(user.id)
    assert operator_check is None
    assert_same_password(updated_user.password_hash, user_password)



    
    








