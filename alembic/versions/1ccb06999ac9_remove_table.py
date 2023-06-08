"""remove table

Revision ID: 1ccb06999ac9
Revises: f2f170841888
Create Date: 2023-06-01 17:00:39.172653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ccb06999ac9'
down_revision = 'f2f170841888'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('alembic_version')
    op.drop_table('author')
    op.drop_table('book')
    # Thêm các lệnh xóa bảng khác


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###