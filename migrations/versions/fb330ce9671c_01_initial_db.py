"""01_initial-db

Revision ID: fb330ce9671c
Revises: a3f3ff457cf9
Create Date: 2023-10-01 22:49:33.023819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb330ce9671c'
down_revision = 'a3f3ff457cf9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('urls', sa.Column('deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('urls', 'deleted')
    # ### end Alembic commands ###
