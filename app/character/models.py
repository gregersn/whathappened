import logging
import json
from functools import reduce
from datetime import datetime
import base64
import io
from PIL import Image

from app import db


logger = logging.getLogger(__name__)


def fix_image(imagedata: str) -> str:
    imagetype, imagedata = imagedata.split(',')
    decoded = base64.b64decode(imagedata)
    buf = io.BytesIO(decoded)
    img = Image.open(buf).convert('RGB')
    img.thumbnail((192, 192))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


class Character(db.Model):
    __tablename__ = 'charactersheet'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))

    def __repr__(self):
        return '<Character {}>'.format(self.title)

    def __init__(self, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self._data = None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': json.loads(self.body),
            'timestamp': self.timestamp,
            'user_id': self.user_id
        }

    def get_sheet(self):
        return json.loads(self.body)

    @property
    def data(self):
        if not hasattr(self, '_data') or self._data is None:
            self._data = json.loads(self.body)

        return self._data

    @property
    def name(self):
        return self.data['personalia']['Name']

    @property
    def age(self):
        return self.data['personalia']['Age']

    @property
    def portrait(self):
        return self.data['personalia']['Portrait']

    @property
    def description(self):
        return self.data['personalia']['Occupation']

    def check_data(self):
        pass

    def attribute(self, *args):
        self.check_data()

        path = args[0]

        val = reduce(lambda x, y: x.get(y, None) if x is not None else None,
                     path.split("."),
                     self.data)

        return val

    def set_attribute(self, attribute):
        """Set a specific attribute."""
        self.check_data()

        if attribute.get('type', None) == 'skill':
            logger.debug("Set a skill")
            skill = attribute['field']
            subfield = attribute.get('subfield', None)
            value = attribute.get('value')
            skill = self.skill(skill, subfield)
            skill['value'] = value

        elif attribute.get('type', None) == 'skillcheck':
            logger.debug("Check a skill")
            skill = attribute['field']
            subfield = attribute.get('subfield', None)
            check = attribute.get('value', False)
            skill = self.skill(skill, subfield)
            skill['checked'] = check

        elif attribute.get('type', None) == 'occupationcheck':
            logger.debug("Mark occupation skill")
            skill = attribute['field']
            subfield = attribute.get('subfield', None)
            check = attribute.get('value', False)
            skill = self.skill(skill, subfield)
            skill['occupation'] = check

        elif attribute.get('type', None) == 'portrait':
            logger.debug("Set portrait")
            data = attribute.get('value', None)
            self.set_portrait(data)
        else:
            logger.debug("Set some other attribute")
            s = reduce(lambda x, y: x[y], attribute['field'].split(".")[:-1],
                       self.data)
            s[attribute['field'].split(".")[-1]] = attribute['value']

    def store_data(self):
        """Put loaded data back into JSON."""
        self.check_data()
        self.body = json.dumps(self.data, indent=4)

    def skill(self, skill, subskill=None):
        """Return a single skill, or something."""
        self.check_data()
        skills = self.skills()
        if subskill == 'None':
            subskill = None

        for s in skills:
            if s['name'] == skill:
                if subskill is not None and 'subskills' not in s:
                    return None
                if subskill is not None:
                    for ss in s['subskills']:
                        if ss['name'] == subskill:
                            return ss
                    logger.debug(f"Did not find subskill {skill}, {subskill}")
                    return None
                return s

        logger.debug(f"Did not find {skill}, {subskill}")
        return None

    def skills(self, *args):
        """Return a list of skills."""
        self.check_data()
        return self.data['skills']

    def add_skill(self, skillname, value="1"):
        self.check_data()

        if self.skill(skillname) is not None:
            raise ValueError(f"Skill {skillname} already exists.")

        self.data['skills'].append({"name": skillname, "value": str(value)})
        if isinstance(self.data['skills'], list):
            self.data['skills'].sort(key=lambda x: x['name'])

    def add_subskill(self, name, parent):
        self.check_data()
        value = self.skill(parent)['value']
        logger.debug("Try to add subskill")
        logger.debug(f"Name: {name}, parent {parent}, value {value}")
        if self.skill(parent, name) is not None:
            raise ValueError(f"Subskill {name} in {parent} already exists.")

        skill = self.skill(parent)
        if 'subskills' not in skill:
            skill['subskills'] = []
        skill['subskills'].append({
            'name': name,
            'value': value
        })

    def set_portrait(self, data):
        self.check_data()
        self.data['personalia']['Portrait'] = fix_image(data)
        return self.portrait

    @property
    def gametype(self):
        self.check_data()
        return self.data['meta']['GameType']
