"""Added some fields

Revision ID: 41989ca4c1b4
Revises: 643d633eea8b
Create Date: 2025-02-21 16:34:33.888057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41989ca4c1b4'
down_revision: Union[str, None] = '643d633eea8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('analysis', sa.Column('ratio_down', sa.Float(), nullable=True))
    op.add_column('analysis', sa.Column('final_data', sa.String(length=255), nullable=True))
    op.add_column('analysis', sa.Column('diffential_data', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('analysis', 'diffential_data')
    op.drop_column('analysis', 'final_data')
    op.drop_column('analysis', 'ratio_down')
    # ### end Alembic commands ###
