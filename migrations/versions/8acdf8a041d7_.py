"""empty message

Revision ID: 8acdf8a041d7
Revises: acf3d03694f2
Create Date: 2022-08-10 17:33:38.160474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8acdf8a041d7'
down_revision = 'acf3d03694f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product', sa.Column('is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product', 'is_active')
    # ### end Alembic commands ###