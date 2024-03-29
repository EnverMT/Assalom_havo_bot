"""musor_ls st2

Revision ID: b66407b36281
Revises: c55bdc80a800
Create Date: 2023-03-02 10:34:30.400805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b66407b36281'
down_revision = 'c55bdc80a800'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('address', sa.Column('musor_ls', sa.String(length=30), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('address', 'musor_ls')
    # ### end Alembic commands ###
