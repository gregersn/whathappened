"""Rename usertable

Revision ID: 27799ac97853
Revises: 186d10393f49
Create Date: 2021-01-23 16:00:15.337409

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "27799ac97853"
down_revision = "186d10393f49"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_index("ix_user_email")
        batch_op.drop_index("ix_user_username")

    op.rename_table("user", "user_account")

    with op.batch_alter_table("user_account", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_user_account_email"), ["email"], unique=True
        )
        batch_op.create_index(
            batch_op.f("ix_user_account_username"), ["username"], unique=True
        )

    with op.batch_alter_table("eventlog", schema=None) as batch_op:
        batch_op.drop_constraint("fk_eventlog_user_id_user", type_="foreignkey")
        batch_op.create_foreign_key(
            batch_op.f("fk_eventlog_user_id_user_account"),
            "user_account",
            ["user_id"],
            ["id"],
        )

    with op.batch_alter_table("user_profile", schema=None) as batch_op:
        batch_op.drop_constraint("fk_user_profile_user_id_user", type_="foreignkey")
        batch_op.create_foreign_key(
            batch_op.f("fk_user_profile_user_id_user_account"),
            "user_account",
            ["user_id"],
            ["id"],
        )

    with op.batch_alter_table("user_roles", schema=None) as batch_op:
        batch_op.drop_constraint("fk_user_roles_user_id_user", type_="foreignkey")
        batch_op.create_foreign_key(
            batch_op.f("fk_user_roles_user_id_user_account"),
            "user_account",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user_roles", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_user_roles_user_id_user_account"), type_="foreignkey"
        )

    with op.batch_alter_table("user_profile", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_user_profile_user_id_user_account"), type_="foreignkey"
        )

    with op.batch_alter_table("eventlog", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_eventlog_user_id_user_account"), type_="foreignkey"
        )

    with op.batch_alter_table("user_account", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_account_username"))
        batch_op.drop_index(batch_op.f("ix_user_account_email"))

    op.rename_table("user_account", "user")

    with op.batch_alter_table("user_roles", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_user_roles_user_id_user",
            "user",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("user_profile", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_user_profile_user_id_user", "user", ["user_id"], ["id"]
        )

    with op.batch_alter_table("eventlog", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_eventlog_user_id_user", "user", ["user_id"], ["id"]
        )

    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.create_index("ix_user_username", ["username"], unique=True)
        batch_op.create_index("ix_user_email", ["email"], unique=True)

    # ### end Alembic commands ###
