"""Added new fields

Revision ID: b93dc4c29b32
Revises: 26974f6bfd67
Create Date: 2025-03-12 10:54:09.015593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b93dc4c29b32'
down_revision: Union[str, None] = '26974f6bfd67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('analysis', sa.Column('direct_differential', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('analysis', 'direct_differential')
    # ### end Alembic commands ###
