"""drop people_pictures table

Revision ID: 465885e83288
Revises: 06751bf6b3d4
Create Date: 2026-03-20 17:15:02.676101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '465885e83288'
down_revision: Union[str, Sequence[str], None] = '06751bf6b3d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('people_pictures')


def downgrade() -> None:
    op.create_table(
        'people_pictures',
        sa.Column('person_id', sa.Integer(), nullable=False),
        sa.Column('picture_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['person_id'], ['people.id']),
        sa.ForeignKeyConstraint(['picture_id'], ['pictures.id']),
        sa.PrimaryKeyConstraint('person_id', 'picture_id'),
    )
