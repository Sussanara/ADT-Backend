"""empty message

Revision ID: acf3d03694f2
Revises: a803b1353f90
Create Date: 2022-08-10 11:57:02.047160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'acf3d03694f2'
down_revision = 'a803b1353f90'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('admin', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('admin', 'is_active')
    # ### end Alembic commands ###