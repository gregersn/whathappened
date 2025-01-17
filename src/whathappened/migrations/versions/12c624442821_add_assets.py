"""Add assets

Revision ID: 12c624442821
Revises: f047bb8f937f
Create Date: 2020-10-14 16:32:12.011489

"""

from alembic import op
import sqlalchemy as sa
from whathappened.core.database.fields import GUID


# revision identifiers, used by Alembic.
revision = "12c624442821"
down_revision = "f047bb8f937f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "asset_folder",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("parent_id", GUID(), nullable=True),
        sa.Column("title", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user_profile.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["asset_folder.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "asset",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("filename", sa.String(length=128), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("folder_id", GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["folder_id"],
            ["asset_folder.id"],
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user_profile.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("asset")
    op.drop_table("asset_folder")
    # ### end Alembic commands ###
