"""merge heads bc21107894a0 + f7b3c5d9e2a1

Revision ID: f5bc36f596a0
Revises: bc21107894a0, f7b3c5d9e2a1
Create Date: 2026-06-01 17:37:14.889762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5bc36f596a0'
down_revision = ('bc21107894a0', 'f7b3c5d9e2a1')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
