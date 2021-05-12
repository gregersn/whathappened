import enum
from flask import url_for
from datetime import datetime
from sqlalchemy.orm import backref, relationship

from sqlalchemy.sql.schema import ForeignKey, Table, Column
from sqlalchemy.sql.sqltypes import Boolean, DateTime
from sqlalchemy.sql.sqltypes import Enum, Integer, String, Text
from app.database import Base, BaseModel
from app.content.mixins import BaseContent

campaign_players = Table('campaign_players',
                         Base.metadata,
                         Column('player_id',
                                Integer,
                                ForeignKey('user_profile.id'),
                                primary_key=True),
                         Column('campaign_id',
                                Integer,
                                ForeignKey('campaign.id'),
                                primary_key=True))

campaign_characters = Table('campaign_characters',
                            Base.metadata,
                            Column('character_id',
                                   Integer,
                                   ForeignKey('charactersheet.id'),
                                   primary_key=True),
                            Column('campaign_id',
                                   Integer,
                                   ForeignKey('campaign.id'),
                                   primary_key=True))


class Campaign(BaseModel, BaseContent):
    __tablename__ = "campaign"
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    description = Column(Text)

    # Owner of the campaign (GM)
    user_id = Column(Integer, ForeignKey('user_profile.id'))
    user = relationship('UserProfile', backref=backref(
        'campaigns', lazy='dynamic'))

    # The players in a campaign
    players = relationship('UserProfile',
                           secondary=campaign_players,
                           lazy='dynamic',
                           backref=backref('campaigns_as_player',
                                           lazy=True))
    # Characters added to the campaign
    characters = relationship('Character',
                              secondary=campaign_characters,
                              lazy='dynamic',
                              backref=backref('campaigns', lazy=True))

    # NPCs added to campaign
    NPCs = relationship(
        "NPC", back_populates='campaign', lazy='dynamic')

    # Handouts added to campaign
    handouts = relationship("Handout",
                            back_populates='campaign',
                            lazy='dynamic')

    # Handout groups for the campaign
    handout_groups = relationship("HandoutGroup",
                                  back_populates='campaign',
                                  lazy='dynamic')

    # Features used for campaign
    characters_enabled = Column(Boolean, default=True)
    npcs_enabled = Column(Boolean, default=False)
    handouts_enabled = Column(Boolean, default=False)
    messages_enabled = Column(Boolean, default=False)

    folder = relationship('Folder', backref='campaigns')

    @property
    def players_by_id(self):
        return dict((player.id, player) for player in self.players)

    def __repr__(self):
        return '<Campaign {}>'.format(self.title)

    _default_fields = [
        "id",
        "title",
        "description",
        "NPCs",
        'handouts'
    ]


player_handouts = Table('campaign_handouts_to_players',
                        Base.metadata,
                        Column('handout_id',
                               Integer,
                               ForeignKey('campaign_handout.id'),
                               primary_key=True),
                        Column('player_id',
                               Integer,
                               ForeignKey('user_profile.id'),
                               primary_key=True))


class HandoutStatus(enum.Enum):
    draft = "Draft"
    deleted = "Deleted"
    hidden = "Hidden"
    visible = "Visible"


class HandoutGroup(Base):
    __tablename__ = 'campaign_handout_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    campaign_id = Column(Integer, ForeignKey('campaign.id'))
    campaign = relationship("Campaign", back_populates='handout_groups')
    handouts = relationship('Handout',
                            lazy='dynamic',
                            back_populates='group')

    def __repr__(self):
        return f'<Handout Group {self.name}>'


class Handout(BaseModel):
    __tablename__ = 'campaign_handout'
    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    content = Column(Text)
    campaign_id = Column(Integer, ForeignKey('campaign.id'))
    campaign = relationship("Campaign", back_populates='handouts')
    status = Column('status',
                    Enum(HandoutStatus),
                    default=HandoutStatus.draft)

    players = relationship('UserProfile',
                           secondary=player_handouts,
                           lazy='dynamic',
                           backref=backref('campaign_handouts',
                                           lazy=True))
    group_id = Column(Integer,
                      ForeignKey('campaign_handout_group.id'))

    group = relationship('HandoutGroup')

    def __repr__(self):
        return '<Handout {}>'.format(self.title)

    _default_fields = [
        'id',
        'title'
    ]

    @property
    def url(self):
        return url_for('campaign.handout_view',
                       campaign_id=self.campaign.id,
                       handout_id=self.id)


class NPC(BaseModel):
    __tablename__ = 'campaign_npc'

    id = Column(Integer, primary_key=True)

    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=False)
    campaign = relationship('Campaign', back_populates='NPCs')

    character_id = Column(Integer, ForeignKey('charactersheet.id'),
                          nullable=False)
    character = relationship('Character')

    visible = Column(Boolean, default=False)

    _default_fields = [
        'character',
        'visible'
    ]


class Message(BaseModel):
    __tablename__ = 'campaign_message'
    id = Column(Integer, primary_key=True)

    campaign_id = Column(Integer, ForeignKey('campaign.id'), nullable=False)
    campaign = relationship('Campaign',
                            backref=backref('messages', lazy='dynamic'))

    to_id = Column(Integer, ForeignKey('user_profile.id'), nullable=True)
    to = relationship('UserProfile', foreign_keys=[to_id])
    from_id = Column(Integer, ForeignKey('user_profile.id'), nullable=False)
    sender = relationship('UserProfile', foreign_keys=[from_id])

    message = Column(Text)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)

    _default_fields = [
        'timestamp',
        'sender_name',
        'to_name',
        'message',
        'id'
    ]

    @property
    def sender_name(self):
        return self.sender.user.username

    @property
    def to_name(self):
        return self.to.user.username if self.to and self.to.user else "All"
