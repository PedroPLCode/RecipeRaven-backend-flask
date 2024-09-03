"""empty message

Revision ID: 4ac8cc3e773c
Revises: cfd08f6dd5bb
Create Date: 2024-09-02 21:42:19.171173

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ac8cc3e773c'
down_revision = 'cfd08f6dd5bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment_hate_it', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('comment_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('comment_like_it', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('comment_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('news_hate_it', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('news_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('news_like_it', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('news_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('post_hate_it', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('post_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('post_like_it', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('post_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('reaction_hate_it', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('reaction_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('reaction_like_it', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('reaction_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reaction_like_it', schema=None) as batch_op:
        batch_op.alter_column('reaction_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('reaction_hate_it', schema=None) as batch_op:
        batch_op.alter_column('reaction_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('post_like_it', schema=None) as batch_op:
        batch_op.alter_column('post_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('post_hate_it', schema=None) as batch_op:
        batch_op.alter_column('post_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('news_like_it', schema=None) as batch_op:
        batch_op.alter_column('news_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('news_hate_it', schema=None) as batch_op:
        batch_op.alter_column('news_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('comment_like_it', schema=None) as batch_op:
        batch_op.alter_column('comment_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('comment_hate_it', schema=None) as batch_op:
        batch_op.alter_column('comment_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
