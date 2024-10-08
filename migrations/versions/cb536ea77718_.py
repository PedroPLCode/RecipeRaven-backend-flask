"""empty message

Revision ID: cb536ea77718
Revises: 9a65cd082c22
Create Date: 2024-07-15 21:04:55.210872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb536ea77718'
down_revision = '9a65cd082c22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('original_google_picture', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('original_google_picture')

    # ### end Alembic commands ###
