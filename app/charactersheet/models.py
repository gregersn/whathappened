import json
from datetime import datetime

from app import db


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    body = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))

    def __repr__(self):
        return '<Character {}>'.format(self.title)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': json.loads(self.body),
            'timestamp': self.timestamp,
            'user_id': self.user_id
        }
