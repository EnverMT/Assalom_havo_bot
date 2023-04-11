"""protected chats bigint

Revision ID: d3d535d89929
Revises: 4a09f234cdb9
Create Date: 2023-04-11 14:40:22.035975

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3d535d89929'
down_revision = '4a09f234cdb9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('protected_chats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('protected_chats')
    # ### end Alembic commands ###
