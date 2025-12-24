import pytest
import app.database as data


@pytest.mark.usefixtures("c")
def test_delete_nonexistent_office(c, monkeypatch):
    ''' Test deleting a non-existent office.
        The test ensures that the appropriate error message is returned.
    '''

    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices2.current_user', current_user)

    # attempt to delete a non-existent office
    url = '/delete_an_office'
    response = c.post(url, json={'office_id': 99999})  # assuming this ID does not exist

    assert response.status_code == 404
    data_response = response.get_json()
    assert data_response['status'] == 'error'
    assert data_response['message'] == 'Office not found'

@pytest.mark.usefixtures("c")
def test_delete_office_unauthorized(c, monkeypatch):
    ''' Test deleting an office with an unauthorized user.
        The test ensures that the appropriate error message is returned.
    '''

    class user:
        def __init__(self):
            self.role_id = 2  # non-admin role
    current_user = user()
    monkeypatch.setattr('app.views.offices2.current_user', current_user)

    # attempt to delete an office
    url = '/delete_an_office'
    response = c.post(url, json={'office_id': 1})  # office_id can be any value

    assert response.status_code == 403
    data_response = response.get_json()
    assert data_response['status'] == 'error'
    assert data_response['message'] == 'Unauthorized'

@pytest.mark.usefixtures("c")
def test_delete_office_no_id(c, monkeypatch):
    ''' Test deleting an office without providing an office ID.
        The test ensures that the appropriate error message is returned.
    '''

    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices2.current_user', current_user)

    # attempt to delete an office without providing an ID
    url = '/delete_an_office'
    response = c.post(url, json={})  # no office_id provided

    assert response.status_code == 400
    data_response = response.get_json()
    assert data_response['status'] == 'error'
    assert data_response['message'] == 'Office ID is required'

@pytest.mark.usefixtures("c")
def test_delete_office_with_tickets_error(c, monkeypatch):
    ''' Test deleting an office that has active tickets.
        The test ensures that the appropriate error message is returned.
    '''

    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices2.current_user', current_user)

    # create a test office
    test_office = data.Office(name="Test Office With Tickets")
    data.db.session.add(test_office)
    data.db.session.commit()
    fetched_office = data.Office.query.filter_by(name="Test Office With Tickets").first()
    assert fetched_office is not None

    #create a task
    test_task = data.Task(name="Test Task")
    data.db.session.add(test_task)
    data.db.session.commit()
    fetched_task = data.Task.query.filter_by(name="Test Task").first()
    assert fetched_task is not None

    # create a ticket associated with the office
    data.Serial.create_new_ticket(office=fetched_office,task=fetched_task,name_or_number="Test Ticket")

    # attempt to delete the office via the endpoint
    url = '/delete_an_office'
    response = c.post(url, json={'office_id': fetched_office.id})

    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response['status'] == 'error'
    assert data_response['message'] == 'Cannot delete office with active tickets'
    
@pytest.mark.usefixtures("c")
def test_delete_an_office_with_tasks_and_operators_no_error(c,monkeypatch):
    ''' Test deleting an office that has operators assigned to it.
        The test ensures that the office is deleted without errors,
        and that the associated operators are also removed due to cascade delete.
    '''

    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices2.current_user', current_user)
    
    #create a test office
    test_office = data.Office(name="Test Office")
    data.db.session.add(test_office)
    data.db.session.commit()
    fetched_office = data.Office.query.filter_by(name="Test Office").first()
    assert fetched_office is not None

    #create a new task 
    test_task = data.Task(name="Test Task")
    data.db.session.add(test_task)
    data.db.session.commit()
    fetched_task = data.Task.query.filter_by(name="Test Task").first()
    assert fetched_task is not None

    #attach task to the office
    fetched_office.tasks.append(fetched_task)
    data.db.session.commit()
    fetched_office = data.Office.query.filter_by(name="Test Office").first()
    assert fetched_task in fetched_office.tasks

    #create a new user

    test_user = data.User(name="operator_user",password="password", role_id=3)  # role_id=3 for operator
    data.db.session.add(test_user)
    data.db.session.commit()
    fetched_user = data.User.query.filter_by(name="operator_user").first()
    assert fetched_user is not None

    # assign the user as an operator to the test office
    operator = data.Operators(id=fetched_user.id, office_id=fetched_office.id)
    data.db.session.add(operator)
    data.db.session.commit()
    fetched_operator = data.Operators.query.filter_by(id=fetched_user.id, office_id=fetched_office.id).first()
    assert fetched_operator is not None

    # check if the operator still exists using raw sql query
    result = data.db.session.execute(f"SELECT * FROM operators WHERE id={fetched_user.id}").fetchone()
    assert result is not None

    #check if the task still exists using raw sql query
    result = data.db.session.execute(f"SELECT * FROM tasks WHERE id={fetched_task.id}").fetchone()
    assert result is not None


    # delete the office via the endpoint
    # it should work due to cascade delete in operators
    url = '/delete_an_office'
    response = c.post(url, json={'office_id': fetched_office.id})
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response['status'] == 'success'
    assert data_response['message'] == 'Office deleted successfully'
    # check if the office still exists using raw sql query
    result = data.db.session.execute(f"SELECT * FROM offices WHERE id={fetched_office.id}").fetchone()  
    assert result is None
    # check if the operator still exists using raw sql query
    result = data.db.session.execute(f"SELECT * FROM operators WHERE id={fetched_user.id}").fetchone()
    assert result is None

    #check if the task still exists using raw sql query
    result = data.db.session.execute(f"SELECT * FROM tasks WHERE id={fetched_task.id}").fetchone()
    assert result is None



@pytest.mark.usefixtures("c")
def test_delete_an_office_tasks_of_other_offices_not_deleted(c,monkeypatch):
    ''' Tasks associated with other offices too should not be deleted when an office is deleted.
        This test ensures that only tasks exclusively linked to the deleted office are removed.
    '''

    class user:
        def __init__(self):
            self.role_id = 1
    current_user = user()
    monkeypatch.setattr('app.views.offices2.current_user', current_user)

    #create two test offices
    test_office1 = data.Office(name="Test Office 1")
    test_office2 = data.Office(name="Test Office 2")
    data.db.session.add(test_office1)
    data.db.session.add(test_office2)
    data.db.session.commit()
    fetched_office1 = data.Office.query.filter_by(name="Test Office 1").first()
    fetched_office2 = data.Office.query.filter_by(name="Test Office 2").first()
    assert fetched_office1 is not None
    assert fetched_office2 is not None

    #create a new task assigned to both offices
    test_task = data.Task(name="Shared Task")
    data.db.session.add(test_task)
    data.db.session.commit()

    #create task only for office to be deleted
    test_task2 = data.Task(name="Exclusive Task")
    data.db.session.add(test_task2)
    data.db.session.commit()
    fetched_exclusive_task = data.Task.query.filter_by(name="Exclusive Task").first()
    assert fetched_exclusive_task is not None

    fetched_shared_task = data.Task.query.filter_by(name="Shared Task").first()
    assert fetched_shared_task is not None

    #attach the shared task to both offices
    fetched_office1.tasks.append(fetched_shared_task)
    fetched_office2.tasks.append(fetched_shared_task)
    data.db.session.commit()
    #attach the exclusive task to only office1
    fetched_office1.tasks.append(fetched_exclusive_task)
    data.db.session.commit()
    
    #assert the task is assigned to both offices
    fetched_office1 = data.Office.query.filter_by(name="Test Office 1").first()
    fetched_office2 = data.Office.query.filter_by(name="Test Office 2").first()
    assert fetched_shared_task in fetched_office1.tasks
    assert fetched_shared_task in fetched_office2.tasks

    url= '/delete_an_office'
    response = c.post(url, json={'office_id': fetched_office1.id})
    assert response.status_code == 200
    data_response = response.get_json()
    assert data_response['status'] == 'success'
    assert data_response['message'] == 'Office deleted successfully'

    # raw sql query to check if office1 still exists
    result = data.db.session.execute(f"SELECT * FROM offices WHERE id={fetched_office1.id}").fetchone()
    assert result is None

    # raw sql query to check if shared task still exists
    result = data.db.session.execute(f"SELECT * FROM tasks WHERE id={fetched_shared_task.id}").fetchone()
    assert result is not None

    # raw sql query to check if exclusive task is deleted
    result = data.db.session.execute(f"SELECT * FROM tasks WHERE id={fetched_exclusive_task.id}").fetchone()
    assert result is None

