"""test empty migration

Revision ID: 976928c277c2
Revises: 8569b9b22f2b
Create Date: 2025-11-15 06:09:03.734740

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '976928c277c2'
down_revision = '8569b9b22f2b'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
