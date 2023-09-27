"""Add metadata naming conventions

Revision ID: ac772b7261d0
Revises: c99e163f4457
Create Date: 2020-11-29 18:20:25.867829

"""
from alembic import op
import sqlalchemy as sa
from alembic import context

# revision identifiers, used by Alembic.
revision = "ac772b7261d0"
down_revision = "c99e163f4457"
branch_labels = None
depends_on = None


def upgrade():
    if context.get_impl().bind.dialect.name == "mysql":
        return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("roles", schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f("uq_roles_name"), ["name"])

    # ### end Alembic commands ###


def downgrade():
    if context.get_impl().bind.dialect.name == "mysql":
        return
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("roles", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_roles_name"), type_="unique")

    # ### end Alembic commands ###
