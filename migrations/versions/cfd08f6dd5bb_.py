"""empty message

Revision ID: cfd08f6dd5bb
Revises: b7e4ad52afa8
Create Date: 2024-08-29 22:15:01.008112

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfd08f6dd5bb'
down_revision = 'b7e4ad52afa8'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('email_confirmed', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()))

def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('email_confirmed')
