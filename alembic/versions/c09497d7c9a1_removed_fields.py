"""removed fields

Revision ID: c09497d7c9a1
Revises: d921104adfda
Create Date: 2025-02-10 12:42:31.395370

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'c09497d7c9a1'
down_revision: Union[str, None] = 'd921104adfda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('analysis', 'file_type')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('analysis', sa.Column('file_type', mysql.VARCHAR(length=50), nullable=True))
    # ### end Alembic commands ###
