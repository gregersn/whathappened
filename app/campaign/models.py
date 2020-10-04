from app import db


players = db.Table('campaign_players',
                   db.Column('player_id',
                             db.Integer,
                             db.ForeignKey('user_profile.id'),
                             primary_key=True),
                   db.Column('campaign_id',
                             db.Integer,
                             db.ForeignKey('campaign.id'),
                             primary_key=True))

characters = db.Table('campaign_characters',
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
    players = db.relationship('UserProfile',
                              secondary=players,
                              lazy='dynamic',
                              backref=db.backref('campaigns_as_player',
                                                 lazy=True))
    characters = db.relationship('Character',
                                 secondary=characters,
                                 lazy='dynamic',
                                 backref=db.backref('campaigns', lazy=True))

    def __repr__(self):
        return '<Campaign {}>'.format(self.title)
