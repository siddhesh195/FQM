import pytest
from app.middleware import db




@pytest.mark.usefixtures('c')
def test_db():

    # make new user
    from app.database import User
    db.session.add(User(name='testuser',password='testpass',role_id=1))
    db.session.commit()
    u = User.query.filter_by(name='testuser').first()
    assert u is not None
    assert u.name == 'testuser'