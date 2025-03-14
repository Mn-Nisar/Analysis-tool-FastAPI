"""Added new fields

Revision ID: 0089349c2169
Revises: c09497d7c9a1
Create Date: 2025-02-11 13:43:56.647125

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0089349c2169'
down_revision: Union[str, None] = 'c09497d7c9a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('analysis', sa.Column('index_col', sa.String(length=255), nullable=True))
    op.add_column('analysis', sa.Column('normalized_data', sa.String(length=255), nullable=True))
    op.add_column('analysis', sa.Column('resedue_data', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('analysis', 'resedue_data')
    op.drop_column('analysis', 'normalized_data')
    op.drop_column('analysis', 'index_col')
    # ### end Alembic commands ###
