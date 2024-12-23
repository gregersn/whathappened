"""Add character campaign association settings.

Revision ID: 6f4e81e899a3
Revises: 155b3a996ca1
Create Date: 2024-12-17 19:47:43.188390

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6f4e81e899a3"
down_revision = "155b3a996ca1"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("campaign_characters", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "editable_by_gm",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "share_with_players",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "group_sheet", sa.Boolean(), nullable=False, server_default=sa.false()
            )
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("campaign_characters", schema=None) as batch_op:
        batch_op.drop_column("group_sheet")
        batch_op.drop_column("share_with_players")
        batch_op.drop_column("editable_by_gm")

    # ### end Alembic commands ###
