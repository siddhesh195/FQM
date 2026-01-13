import pytest

from app.helpers import get_number_of_active_tickets_office_cached
import app.database as data
from tests.helpers.helpers import (
    add_and_assert_office,
    add_and_assert_common_task,
    add_and_assert_task
)




@pytest.mark.usefixtures('c')
def test_tokens_common_office(c, monkeypatch):
    """

    Test to verify that for common task, tokens added are correct.
    Only the office for which token is added should display and allow to pull the token.
    
    """
    # create a new token by calling the API: @core.route('/serial/<int:t_id>/<int:office_id>', methods=['GET', 'POST'])

    # first, create two offices by calling : @offices.route('/add_office', methods=['POST', 'GET'])

    # then create a common task by calling: @tasks.route('/add_common_task', methods=['POST'])

    # finally, call the token API for the common task for one of the offices created above

    # Create two offices
    class User:
        def __init__(self):
            self.role_id = 1  # Admin role

    user = User()

    monkeypatch.setattr('app.views.offices.current_user', user)
    monkeypatch.setattr('app.views.tasks.current_user', user)

    office1 = add_and_assert_office('Office A', 'A', c)
    office2 = add_and_assert_office('Office B', 'B', c)

    office_ids = [office1.id, office2.id]

    # Create a common task associated with both offices
    task = add_and_assert_common_task('Common Task 1', office_ids, c)
    
    # Now, test token retrieval for the common task for office1, follow redirects if any
    token_url_office1 = f'/serial/{task.id}/{office1.id}'
    # add auto=1 to auto generate token
    token_url_office1 += '?auto=1'
    response1 = c.get(token_url_office1)
    
    assert response1.status_code == 200

    assert response1.json['status'] == 'success'
    assert response1.json['message'] == 'Common task added successfully'
    assert 'identifier' in response1.json
    token_identifier1 = response1.json['identifier']
    assert len(token_identifier1)==8  # Assuming identifier is an 8 character string

    #now check if token is generated only for office1 and not for office2
    active_tickets_office1 = get_number_of_active_tickets_office_cached(office1.id)
    active_tickets_office2 = get_number_of_active_tickets_office_cached(office2.id)

    assert active_tickets_office1 == 1
    assert active_tickets_office2 == 0

    # now also check if we can pull the token for office for which token was not generated
    next_ticket_office2 = data.Serial.get_next_ticket(task_id=task.id,
                                              office_id=office2.id)
    
    assert next_ticket_office2 is None

    #now also check if we can pull the token for office1
    next_ticket_office1 = data.Serial.get_next_ticket(task_id=task.id,
                                              office_id=office1.id)
    assert next_ticket_office1 is not None

    if not next_ticket_office1.pull( next_ticket_office1.office_id):
        pytest.fail("Failed to pull the token for office1")


@pytest.mark.usefixtures('c', 'monkeypatch')
def test_tokens_task_With_same_name(c, monkeypatch):
    """
    
    Test to verify that tasks with same name in different offices work correctly.

    """
    # create a new token by calling the API: @core.route('/serial/<int:t_id>/<int:office_id>', methods=['GET', 'POST'])

    # first, create two offices by calling : @offices.route('/add_office', methods=['POST', 'GET'])

    # then create two tasks with same name but in different offices by calling: @tasks.route('/add_task/<int:office_id>', methods=['POST'])

    # finally, call the token API for both tasks created above

    # Create two offices
    class User:
        def __init__(self):
            self.role_id = 1  # Admin role

    user = User()

    monkeypatch.setattr('app.views.offices.current_user', user)
    monkeypatch.setattr('app.views.tasks.current_user', user)

    office1 = add_and_assert_office('Office X', 'X', c)
    office2 = add_and_assert_office('Office Y', 'Y', c)

    # Create two tasks with same name in different offices
    task_name = 'Identical Task Name'
    task1 = add_and_assert_task(task_name, office1.id, c)
    task2 = add_and_assert_task(task_name, office2.id, c)

    #now create token for task1 in office1
    token_url_office1 = f'/serial/{task1.id}/{office1.id}'
    # add auto=1 to auto generate token
    token_url_office1 += '?auto=1'
    response1 = c.get(token_url_office1)
    assert response1.status_code == 200
    assert response1.json['status'] == 'success'
    assert 'identifier' in response1.json
    token_identifier1 = response1.json['identifier']
    assert len(token_identifier1) == 8  # Assuming identifier is an 8 character

    # now check if this token is only for office1 and not for office2
    active_tickets_office1 = get_number_of_active_tickets_office_cached(office1.id)
    active_tickets_office2 = get_number_of_active_tickets_office_cached(office2.id)

    assert active_tickets_office1 == 1
    assert active_tickets_office2 == 0

    #now also check if we can pull the token for office1
    next_ticket_office1 = data.Serial.get_next_ticket(task_id=task1.id,
                                              office_id=office1.id)
    assert next_ticket_office1 is not None

    # Try to pull token for office2, should be None
    next_ticket_office2 = data.Serial.get_next_ticket(task_id=task2.id,
                                              office_id=office2.id)
    assert next_ticket_office2 is None

@pytest.mark.usefixtures('c', 'monkeypatch')
def test_token_with_invalid_office(c, monkeypatch):
    """
    
    Test to verify that requesting a token with an invalid office ID fails gracefully.

    """
    # Create an office and a task first
    class User:
        def __init__(self):
            self.role_id = 1  # Admin role

    user = User()

    monkeypatch.setattr('app.views.offices.current_user', user)
    monkeypatch.setattr('app.views.tasks.current_user', user)

    office = add_and_assert_office('Office Z', 'Z', c)

    
    task = add_and_assert_task('Task for Invalid Office Test', office.id, c)

    # Now, try to get a token for the task but with an invalid office ID
    invalid_office_id = 99999  # Assuming this ID does not exist
    token_url_invalid_office = f'/serial/{task.id}/{invalid_office_id}'
    token_url_invalid_office += '?auto=1'
    
    response = c.get(token_url_invalid_office)
    
    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert 'Office ID not found' in response.json['message']

@pytest.mark.usefixtures('c', 'monkeypatch')
def test_token_with_invalid_task(c, monkeypatch):
    """
    
    Test to verify that requesting a token with an invalid task ID fails gracefully.

    """
    # Create an office first
    class User:
        def __init__(self):
            self.role_id = 1  # Admin role

    user = User()

    monkeypatch.setattr('app.views.offices.current_user', user)
    monkeypatch.setattr('app.views.tasks.current_user', user)
    
    office = add_and_assert_office('Office Z', 'Z', c)

    

    # Now, try to get a token with an invalid task ID
    invalid_task_id = 99999  # Assuming this ID does not exist
    token_url_invalid_task = f'/serial/{invalid_task_id}/{office.id}'
    token_url_invalid_task += '?auto=1'
    
    response = c.get(token_url_invalid_task)
    
    assert response.status_code == 404
    assert response.json['status'] == 'error'
    assert 'Task ID not found' in response.json['message']

@pytest.mark.usefixtures('c', 'monkeypatch')
def test_token_without_office_id(c, monkeypatch):
    """
    
    Test to verify that requesting a token without providing an office ID fails gracefully.

    """
    # Create an office and a task first
    class User:
        def __init__(self):
            self.role_id = 1  # Admin role

    user = User()

    monkeypatch.setattr('app.views.offices.current_user', user)
    monkeypatch.setattr('app.views.tasks.current_user', user)

    office = add_and_assert_office('Office Z', 'Z', c)

    
    task = add_and_assert_task('Task for No Office ID Test', office.id, c)

    # Now, try to get a token for the task but without an office ID
    token_url_no_office = f'/serial/{task.id}'
    token_url_no_office += '?auto=1'
    
    response = c.get(token_url_no_office)
    
    assert response.status_code == 400  
    assert response.json['status'] == 'error'
    assert 'office id is required to generate a new ticket' in response.json['message']


    
    


    

    



    

   