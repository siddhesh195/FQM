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
