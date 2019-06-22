"""empty message

Revision ID: 1d7e4dd2455b
Revises: f6016df2253b
Create Date: 2019-05-14 16:29:31.232584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d7e4dd2455b'
down_revision = 'f6016df2253b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('square_customer_id', sa.String(length=64), nullable=True))
    op.create_unique_constraint(None, 'users', ['square_customer_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'square_customer_id')
    # ### end Alembic commands ###