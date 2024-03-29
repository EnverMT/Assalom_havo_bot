"""protected chat v2

Revision ID: 63dbe6581e4e
Revises: d3d535d89929
Create Date: 2023-04-15 13:06:27.516631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63dbe6581e4e'
down_revision = 'd3d535d89929'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('protected_chats', sa.Column('thread_id', sa.BigInteger(), nullable=True))
    op.alter_column('protected_chats', 'chat_id',
               existing_type=sa.BIGINT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('protected_chats', 'chat_id',
               existing_type=sa.BIGINT(),
               nullable=False)
    op.drop_column('protected_chats', 'thread_id')
    # ### end Alembic commands ###
