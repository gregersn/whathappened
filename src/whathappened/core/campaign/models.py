"""Campaign database models."""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import backref, relationship, Mapped, mapped_column
from sqlalchemy.sql.schema import ForeignKey, Table, Column
from sqlalchemy.sql.sqltypes import DateTime, Enum, Integer, String, Text

from whathappened.core.database.base import Base, BaseModel
from whathappened.core.content.mixins import BaseContent
from whathappened.core.database.models import UserProfile
from whathappened.core.character.models import Character
from whathappened.core.content.models import Folder


campaign_players = Table(
    "campaign_players",
    Base.metadata,
    Column("player_id", Integer, ForeignKey("user_profile.id"), primary_key=True),
    Column("campaign_id", Integer, ForeignKey("campaign.id"), primary_key=True),
)


class CampaignCharacter(BaseModel):
    """How a character is associated with a campaign."""

    __tablename__ = "campaign_characters"

    character_id: Mapped[int] = mapped_column(
        ForeignKey("charactersheet.id"), primary_key=True
    )
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaign.id"), primary_key=True
    )

    editable_by_gm: Mapped[bool] = mapped_column(default=False)
    share_with_players: Mapped[bool] = mapped_column(default=False)
    group_sheet: Mapped[bool] = mapped_column(default=False)

    character: Mapped[Character] = relationship(
        backref=backref("campaign_associations")
    )
    campaign: Mapped["Campaign"] = relationship(back_populates="character_associations")


class Campaign(BaseModel, BaseContent):
    """Campaign information."""

    __tablename__ = "campaign"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Owner of the campaign (GM)
    user_id = mapped_column(ForeignKey("user_profile.id"))
    user: Mapped[UserProfile] = relationship(
        backref=backref("campaigns", lazy="dynamic")
    )

    # The players in a campaign
    players: Mapped[list[UserProfile]] = relationship(
        secondary=campaign_players,
        lazy="dynamic",
        backref=backref("campaigns_as_player", lazy=True),
    )
    # Characters added to the campaign
    characters: Mapped[list["Character"]] = relationship(
        secondary="campaign_characters",
        lazy="dynamic",
        backref=backref("campaigns_as_character", lazy=True),
        viewonly=True,
    )
    character_associations: Mapped[list["CampaignCharacter"]] = relationship(
        back_populates="campaign", cascade="all, delete"
    )

    # NPCs added to campaign
    NPCs: Mapped[list["NPC"]] = relationship(
        back_populates="campaign", lazy="dynamic", cascade="all, delete"
    )

    # Handouts added to campaign
    handouts: Mapped[list["Handout"]] = relationship(
        back_populates="campaign", lazy="dynamic", cascade="all, delete"
    )

    # Handout groups for the campaign
    handout_groups: Mapped[list["HandoutGroup"]] = relationship(
        back_populates="campaign", lazy="dynamic", cascade="all, delete"
    )

    # Features used for campaign
    characters_enabled: Mapped[bool] = mapped_column(default=True, nullable=True)
    npcs_enabled: Mapped[bool] = mapped_column(default=False, nullable=True)
    handouts_enabled: Mapped[bool] = mapped_column(default=False, nullable=True)
    messages_enabled: Mapped[bool] = mapped_column(default=False, nullable=True)

    folder: Mapped["Folder"] = relationship(backref="campaigns")

    @property
    def players_by_id(self):
        """Get all players as a dictionary by id."""
        return dict((player.id, player) for player in self.players)

    def __repr__(self):
        return f"<Campaign {self.title}>"

    _default_fields = ["id", "title", "description", "NPCs", "handouts"]


player_handouts = Table(
    "campaign_handouts_to_players",
    Base.metadata,
    Column("handout_id", Integer, ForeignKey("campaign_handout.id"), primary_key=True),
    Column("player_id", Integer, ForeignKey("user_profile.id"), primary_key=True),
)


class HandoutStatus(enum.Enum):
    """Status of a handout."""

    draft = "Draft"
    deleted = "Deleted"
    hidden = "Hidden"
    visible = "Visible"


class HandoutGroup(Base):
    """A group of handouts."""

    __tablename__ = "campaign_handout_group"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=True)
    campaign_id = mapped_column(ForeignKey("campaign.id"))
    campaign: Mapped[Campaign] = relationship(back_populates="handout_groups")
    handouts: Mapped["Handout"] = relationship(back_populates="group")

    def __repr__(self):
        return f"<Handout Group {self.name}>"


HandoutStatusType: Enum = Enum(
    HandoutStatus,
    name="handoutstatus",
    create_constraint=True,
    metadata=Base.metadata,
    validate_strings=True,
)


class Handout(BaseModel):
    """A handout."""

    __tablename__ = "campaign_handout"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign.id"), nullable=True)
    campaign: Mapped[Campaign] = relationship(back_populates="handouts")
    status: Mapped[HandoutStatus] = mapped_column(
        default=HandoutStatus.draft, nullable=True
    )

    players: Mapped[list[UserProfile]] = relationship(
        secondary=player_handouts,
        lazy="dynamic",
        backref=backref("campaign_handouts", lazy=True),
    )
    group_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("campaign_handout_group.id"), nullable=True
    )

    group: Mapped[HandoutGroup] = relationship()

    def __repr__(self):
        return f"<Handout {self.title}>"

    _default_fields = ["id", "title"]


class NPC(BaseModel):
    """An NPC."""

    __tablename__ = "campaign_npc"

    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign.id"), nullable=False)
    campaign: Mapped[Campaign] = relationship(back_populates="NPCs")

    character_id: Mapped[int] = mapped_column(
        ForeignKey("charactersheet.id"), nullable=False
    )
    character: Mapped[Character] = relationship(backref="npc", lazy=True)

    visible: Mapped[bool] = mapped_column(default=False, nullable=True)

    _default_fields = ["character", "visible"]


class Message(BaseModel):
    """A message."""

    __tablename__ = "campaign_message"
    id: Mapped[int] = mapped_column(primary_key=True)

    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign.id"), nullable=False)
    campaign: Mapped[Campaign] = relationship(
        backref=backref("messages", lazy="dynamic", cascade="all, delete")
    )

    to_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"), nullable=True)
    to: Mapped[UserProfile] = relationship(foreign_keys=[to_id])
    from_id: Mapped[int] = mapped_column(ForeignKey("user_profile.id"), nullable=False)
    sender: Mapped[UserProfile] = relationship(foreign_keys=[from_id])

    message: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, index=True, default=datetime.utcnow, nullable=True
    )

    _default_fields = ["timestamp", "sender_name", "to_name", "message", "id"]

    @property
    def sender_name(self):
        """Name of message sender."""
        return self.sender.user.username

    @property
    def to_name(self):
        """Name of message recipient."""
        return self.to.user.username if self.to and self.to.user else "All"
