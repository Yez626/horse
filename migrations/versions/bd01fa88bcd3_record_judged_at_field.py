"""record judged_at field

Revision ID: bd01fa88bcd3
Revises: ca13cabaea42
Create Date: 2022-05-07 18:18:53.451576

"""
import sqlalchemy as sa
import sqlmodel
import sqlmodel.sql.sqltypes
from alembic import op

# revision identifiers, used by Alembic.
revision = "bd01fa88bcd3"
down_revision = "ca13cabaea42"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("records", sa.Column("judged_at", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("records", "judged_at")
    # ### end Alembic commands ###
