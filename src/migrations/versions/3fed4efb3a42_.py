"""empty message

Revision ID: 3fed4efb3a42
Revises: cbc4fdb8b23a
Create Date: 2020-09-23 12:25:40.263466

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fed4efb3a42'
down_revision = 'cbc4fdb8b23a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('disabled', sa.Boolean(), nullable=True))
    op.execute("UPDATE \"user\" SET disabled='f';")
    op.alter_column('user', 'disabled',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'disabled')
    # ### end Alembic commands ###
