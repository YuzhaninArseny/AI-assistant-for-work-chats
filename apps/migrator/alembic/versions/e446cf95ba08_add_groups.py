"""Add groups

Revision ID: e446cf95ba08
Revises: 51302249d6a2
Create Date: 2025-12-05 14:58:56.998993

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e446cf95ba08'
down_revision: Union[str, Sequence[str], None] = '51302249d6a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('group',
                    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
                    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('group_pkey'))
                    )
    op.create_table('groupmembership',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.Column('group_id', sa.BIGINT(), autoincrement=False, nullable=False),
                    sa.PrimaryKeyConstraint('id', name=op.f('groupmembership_pkey'))
                    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('groupmembership')
    op.drop_table('group')
