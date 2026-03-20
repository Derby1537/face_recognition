"""add tolerance to face_encodings

Revision ID: 06751bf6b3d4
Revises: 
Create Date: 2026-03-20 17:13:31.635977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '06751bf6b3d4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('face_encodings', sa.Column('tolerance', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('face_encodings', 'tolerance')
