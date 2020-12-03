"""empty message

Revision ID: a849cdbac9c4
Revises: f510556f33e1
Create Date: 2020-12-03 10:10:07.193471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a849cdbac9c4'
down_revision = 'f510556f33e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('role', sa.VARCHAR(), nullable=True))
    # ### end Alembic commands ###
