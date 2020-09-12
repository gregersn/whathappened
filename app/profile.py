from flask import (
    Blueprint, render_template
)
from flask_login import login_required, current_user

from app import db, assets

bp = Blueprint('profile', __name__)

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="profile")
    
    characters = db.relationship('Character', backref='player', lazy='dynamic')

    def __repr__(self):
        return f'<UserProfile {self.user_id}>'

@bp.route('/')
@login_required
def index():
    user_profile = UserProfile.query.get(current_user.id)

    if user_profile is None:
        user_profile = UserProfile(user_id=current_user.id)
        db.session.add(user_profile)
        db.session.commit()

    print(user_profile)
    print(user_profile.characters.all())
    return render_template('profile/index.html.jinja', profile=user_profile)