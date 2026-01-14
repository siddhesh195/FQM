import pytest

from tests.helpers.helpers import (
    add_and_assert_office,
    add_and_assert_common_task,
    add_and_assert_task
)



@pytest.mark.usefixtures('c')
def test_create_token_for_common_task(c,monkeypatch):

    """
    create token for common task successfully
    
    """
    class User:
        def __init__(self):
            self.role_id = 1  # Admin role

    user = User()
    monkeypatch.setattr('app.views.offices.current_user', user)
    monkeypatch.setattr('app.views.tasks.current_user', user)
    
    # create two offices
    office1 = add_and_assert_office('Office A', 'A', c)
    office2 = add_and_assert_office('Office B', 'B', c)
    

    # create a common task associated with both offices
    office_ids = [office1.id, office2.id]
    task = add_and_assert_common_task('Common Task 1', office_ids, c)

    # now, create token for the common task for office1
    token_url_office1 = f'/serial/{task.id}/{office1.id}'
    # add auto=1 to auto generate token
    token_url_office1 += '?auto=1'
    response1 = c.get(token_url_office1)
    assert response1.status_code == 200
    assert response1.json['status'] == 'success'
    assert 'identifier' in response1.json
    token_identifier1 = response1.json['identifier']
    assert 'message' in response1.json
    assert response1.json['message'] == 'Ticket generated successfully'
    assert len(token_identifier1)==8  # assuming identifier is an 8 character string
