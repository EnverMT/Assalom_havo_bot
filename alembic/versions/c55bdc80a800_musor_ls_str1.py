"""musor_ls str1

Revision ID: c55bdc80a800
Revises: 3610fcb3cc1a
Create Date: 2023-03-02 10:34:00.034981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c55bdc80a800'
down_revision = '3610fcb3cc1a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('address', 'musor_ls')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('address', sa.Column('musor_ls', sa.BIGINT(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###