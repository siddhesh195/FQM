import pytest



@pytest.mark.usefixtures('c')
def test_add_office_empty_name_failure(c, monkeypatch):
    """Test to add an office."""

    class User:
        def __init__(self):
            self.role_id = 1 # admin role

    current_user = User()
    monkeypatch.setattr('app.views.offices.current_user', current_user)


    office_data = {
        'name': '',
        'prefix': 'O'
    }
    add_office_url= '/add_office'

    response = c.post(add_office_url, json=office_data)
    assert response.status_code == 400
    assert response.json['status'] == 'error'

    assert 'Form validation failed' in response.json['message']

@pytest.mark.usefixtures('c')
def test_existing_prefix_office_creation_fail(c,monkeypatch):

    class User:
        def __init__(self):
            self.role_id = 1 # admin role

    current_user = User()
    monkeypatch.setattr('app.views.offices.current_user', current_user)
    # add a new office
    name = 'Test Office 1'
    prefix= "Z"

    payload = {
        'name': name,
        'prefix': prefix
    }

    response = c.post('/add_office',json=payload)

    assert response.status == '200 OK'
    response_json = response.get_json()
    assert 'status' in response_json
    assert response_json['status'] == 'success'
    assert 'message' in response_json
    assert response_json['message'] == 'Office added successfully'

    #now add another office with same prefix
    name2 = 'Test Office 2'
    payload2 = {
        'name': name2,
        'prefix': prefix
    }

    response2 = c.post('/add_office',json=payload2)
    assert response2.status_code == 400
    assert response2.json['status'] == 'error'
    assert response2.json['message'] == 'Form validation failed'
    
    
  
