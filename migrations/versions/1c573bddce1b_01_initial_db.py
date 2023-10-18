"""01_initial-db

Revision ID: 1c573bddce1b
Revises: cd422620445a
Create Date: 2023-10-18 01:15:29.532724

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c573bddce1b'
down_revision = 'cd422620445a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('account_id', sa.String(length=96), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'account_id')
    # ### end Alembic commands ###
