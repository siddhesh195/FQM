import pytest
from flask_migrate import upgrade as database_upgrade


@pytest.mark.usefixtures('c')
def test_upgrading_database(c):
    assert database_upgrade() is None
