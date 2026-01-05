import pytest
from sqlalchemy import inspect
from app.middleware import db


@pytest.mark.usefixtures('flask_app')
def test_database_schema_created(flask_app):
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "roles" in tables