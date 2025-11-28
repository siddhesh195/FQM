import pytest


@pytest.mark.usefixtures('c')
def test_display_screen_office_not_found(c,monkeypatch):
    class current_user_class:
        def __init__(self):
            self.role_id=2
    import app.views.core
    current_user = current_user_class()
    monkeypatch.setattr(app.views.core, 'current_user', current_user)

    response = c.get('/display/22', follow_redirects=True)

    assert response.status_code == 404
    response_json = response.get_json()
    assert 'error' in response_json
    assert response_json['error'] == 'Office not found'


@pytest.mark.usefixtures('c')
def test_display_screen_user_not_allowed_to_access_display_html(c,monkeypatch):
    class current_user_class:
        def __init__(self):
            self.role_id=4
    import app.views.core
    current_user = current_user_class()
    monkeypatch.setattr(app.views.core, 'current_user', current_user)

    response = c.get('/display', follow_redirects=True)

    assert response.status_code == 403
    response_json = response.get_json()
    assert 'error' in response_json
    assert response_json['error'] == 'You are not authorized to access display page'


@pytest.mark.usefixtures('c')
def test_display_screen_user_not_allowed_to_access_specific_office_page(c,monkeypatch):
    from app.database import Office
    class current_user_class:
        def __init__(self):
            self.role_id=2
            self.id = 3
    class Operator:
        def __init__(self,id):
            self.id = id
    class FakeOffice_instance:
        _operators= []
        def __init__(self):
            operator1= Operator(6)
            self._operators.append(operator1)
            operator2= Operator(7)
            self._operators.append(operator2)
            operator3= Operator(2)
            self._operators.append(operator3)

            
        @property
        def operators(self):
            return self._operators
        
    class FakeOffice(Office):
        @classmethod
        def get(cls,office_id):
            return FakeOffice_instance()

    
    import app.views.core
    current_user = current_user_class()
    monkeypatch.setattr(app.views.core, 'current_user', current_user)
    monkeypatch.setattr(app.views.core.data, 'Office', FakeOffice)


    response = c.get('/display/3', follow_redirects=True)

    assert response.status_code == 403
    response_json = response.get_json()
    assert 'error' in response_json
    assert response_json['error'] == 'You are not authorized to access display page of this office'

