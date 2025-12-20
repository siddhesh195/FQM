import pytest
import app.database as data




@pytest.mark.usefixtures("c")
def test_delete_an_office_with_operators_no_error(c,monkeypatch):
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

    # attempt to delete the office via the endpoint
    # it should work now due to cascade delete
    url = '/delete_an_office'
    response = c.post(url, json={'office_id': fetched_office.id})

    

    # check if the operator still exists using raw sql query
    result = data.db.session.execute(f"SELECT * FROM operators WHERE id={fetched_user.id} AND office_id={fetched_office.id}").fetchone()
    assert result is None