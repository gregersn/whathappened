"""Add content folders

Revision ID: b10c98640b7c
Revises: a425da83bea3
Create Date: 2021-04-27 22:42:23.571828

"""

from alembic import op
import sqlalchemy as sa
from whathappened.database.fields import GUID

# revision identifiers, used by Alembic.
revision = "b10c98640b7c"
down_revision = "a425da83bea3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "folder",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("parent_id", GUID(), nullable=True),
        sa.Column("title", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user_profile.id"],
            name=op.f("fk_folder_owner_id_user_profile"),
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["folder.id"], name=op.f("fk_folder_parent_id_folder")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_folder")),
    )
    with op.batch_alter_table("campaign", schema=None) as batch_op:
        batch_op.add_column(sa.Column("folder_id", GUID(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f("fk_campaign_folder_id_folder"), "folder", ["folder_id"], ["id"]
        )

    with op.batch_alter_table("charactersheet", schema=None) as batch_op:
        batch_op.add_column(sa.Column("folder_id", GUID(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f("fk_charactersheet_folder_id_folder"),
            "folder",
            ["folder_id"],
            ["id"],
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("charactersheet", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_charactersheet_folder_id_folder"), type_="foreignkey"
        )
        batch_op.drop_column("folder_id")

    with op.batch_alter_table("campaign", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_campaign_folder_id_folder"), type_="foreignkey"
        )
        batch_op.drop_column("folder_id")

    op.drop_table("folder")
    # ### end Alembic commands ###
