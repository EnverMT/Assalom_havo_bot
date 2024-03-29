"""musor_ls added

Revision ID: 54491e3d1ca2
Revises: 59aeba7edc8c
Create Date: 2023-03-02 10:05:41.173953

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54491e3d1ca2'
down_revision = '59aeba7edc8c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('address', sa.Column('musor_ls', sa.BigInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('address', 'musor_ls')
    # ### end Alembic commands ###
