import enum
from flask import url_for
from app import db

campaign_players = db.Table('campaign_players',
                            db.Column('player_id',
                                      db.Integer,
                                      db.ForeignKey('user_profile.id'),
                                      primary_key=True),
                            db.Column('campaign_id',
                                      db.Integer,
                                      db.ForeignKey('campaign.id'),
                                      primary_key=True))

campaign_characters = db.Table('campaign_characters',
                               db.Column('character_id',
                                         db.Integer,
                                         db.ForeignKey('charactersheet.id'),
                                         primary_key=True),
                               db.Column('campaign_id',
                                         db.Integer,
                                         db.ForeignKey('campaign.id'),
                                         primary_key=True))


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
    user = db.relationship("UserProfile", back_populates='campaigns')
    players = db.relationship('UserProfile',
                              secondary=campaign_players,
                              lazy='dynamic',
                              backref=db.backref('campaigns_as_player',
                                                 lazy=True))
    characters = db.relationship('Character',
                                 secondary=campaign_characters,
                                 lazy='dynamic',
                                 backref=db.backref('campaigns', lazy=True))

    handouts = db.relationship("Handout",
                               back_populates='campaign',
                               lazy='dynamic')

    handout_groups = db.relationship("HandoutGroup",
                                     back_populates='campaign',
                                     lazy='dynamic')

    @property
    def players_by_id(self):
        return dict((player.id, player) for player in self.players)

    def __repr__(self):
        return '<Campaign {}>'.format(self.title)


player_handouts = db.Table('campaign_handouts_to_players',
                           db.Column('handout_id',
                                     db.Integer,
                                     db.ForeignKey('campaign_handout.id'),
                                     primary_key=True),
                           db.Column('player_id',
                                     db.Integer,
                                     db.ForeignKey('user_profile.id'),
                                     primary_key=True))


class HandoutStatus(enum.Enum):
    draft = "Draft"
    deleted = "Deleted"
    hidden = "Hidden"
    visible = "Visible"


class HandoutGroup(db.Model):
    __tablename__ = 'campaign_handout_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship("Campaign", back_populates='handout_groups')
    handouts = db.relationship('Handout',
                               lazy='dynamic',
                               back_populates='group')

    def __repr__(self):
        return f'<Handout Group {self.name}>'


class Handout(db.Model):
    __tablename__ = 'campaign_handout'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    content = db.Column(db.Text)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    campaign = db.relationship("Campaign", back_populates='handouts')
    status = db.Column('status',
                       db.Enum(HandoutStatus),
                       default=HandoutStatus.draft)

    players = db.relationship('UserProfile',
                              secondary=player_handouts,
                              lazy='dynamic',
                              backref=db.backref('campaign_handouts',
                                                 lazy=True))

    group_id = db.Column(db.Integer,
                         db.ForeignKey('campaign_handout_group.id'),
                         name="group_id")

    group = db.relationship('HandoutGroup')

    def __repr__(self):
        return '<Handout {}>'.format(self.title)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': url_for('campaign.handout_view', campaign_id=self.campaign.id, handout_id=self.id)
        }
