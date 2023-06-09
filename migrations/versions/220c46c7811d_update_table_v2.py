"""update table v2

Revision ID: 220c46c7811d
Revises: 543a3778d316
Create Date: 2023-06-12 16:43:24.450571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '220c46c7811d'
down_revision = '543a3778d316'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('fullname', sa.String(), nullable=True))
    op.drop_column('users', 'full_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('full_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('users', 'fullname')
    # ### end Alembic commands ###
