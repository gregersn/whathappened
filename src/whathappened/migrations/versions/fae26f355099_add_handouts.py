"""Add handouts

Revision ID: fae26f355099
Revises: 71a3d1badc2e
Create Date: 2020-10-10 10:51:59.883247

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fae26f355099"
down_revision = "71a3d1badc2e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "campaign_handout",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("campaign_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["campaign.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "campaign_handouts_to_players",
        sa.Column("handout_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["handout_id"],
            ["campaign_handout.id"],
        ),
        sa.ForeignKeyConstraint(
            ["player_id"],
            ["user_profile.id"],
        ),
        sa.PrimaryKeyConstraint("handout_id", "player_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("campaign_handouts_to_players")
    op.drop_table("campaign_handout")
    # ### end Alembic commands ###
