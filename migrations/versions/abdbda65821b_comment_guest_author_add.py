"""comment.guest_author ADD

Revision ID: abdbda65821b
Revises: 983cad43a38b
Create Date: 2024-06-11 21:20:34.166999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abdbda65821b'
down_revision = '983cad43a38b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('guest_author', sa.String(length=80), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_column('guest_author')

    # ### end Alembic commands ###
