import json
import logging
from functools import reduce
from jsonschema import Draft7Validator
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime
import base64
import io
from PIL import Image

from app import db

from app.character.coc import schema_file, load_schema

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
    body = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))

    def __repr__(self):
        return '<Character {}>'.format(self.title)

    @property
    def game(self):
        try:
            return (self.body['meta']['GameName'],
                    self.body['meta']['GameType'])
        except Exception as e:
            return None

    def __init__(self, *args, **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self._data = None

    def validate(self, filename=schema_file):
        schema = load_schema(filename)
        v = Draft7Validator(schema)
        return [{'path': "/".join(str(x) for x in e.path),
                 "message": e.message} for e in v.iter_errors(self.body)]

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'timestamp': self.timestamp,
            'user_id': self.user_id
        }

    def get_sheet(self):
        return json.loads(self.body)

    @property
    def name(self):
        return self.body['personalia']['Name']

    @property
    def age(self):
        return self.body['personalia']['Age']

    @property
    def portrait(self):
        return self.body['personalia']['Portrait']

    @property
    def description(self):
        return self.body['personalia']['Occupation']

    def attribute(self, *args):

        path = args[0]

        val = reduce(lambda x, y: x.get(y, None) if x is not None else None,
                     path.split("."),
                     self.body)

        return val

    def set_attribute(self, attribute):
        """Set a specific attribute."""

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
                       self.body)
            s[attribute['field'].split(".")[-1]] = attribute['value']

    def store_data(self):
        """Mark data as modified."""
        flag_modified(self, "body")

    def skill(self, skill, subskill=None):
        """Return a single skill, or something."""
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
        return self.body['skills']

    def add_skill(self, skillname, value="1"):
        if self.skill(skillname) is not None:
            raise ValueError(f"Skill {skillname} already exists.")

        self.body['skills'].append({"name": skillname, "value": str(value)})
        if isinstance(self.body['skills'], list):
            self.body['skills'].sort(key=lambda x: x['name'])

    def add_subskill(self, name, parent):
        value = self.skill(parent)['value']
        start_value = self.skill(parent)['start_value']
        logger.debug("Try to add subskill")
        logger.debug(f"Name: {name}, parent {parent}, value {value}")
        if self.skill(parent, name) is not None:
            raise ValueError(f"Subskill {name} in {parent} already exists.")

        skill = self.skill(parent)
        if 'subskills' not in skill:
            skill['subskills'] = []
        skill['subskills'].append({
            'name': name,
            'value': value,
            'start_value': start_value
        })

    def set_portrait(self, data):
        self.body['personalia']['Portrait'] = fix_image(data)
        return self.portrait

    @property
    def schema_version(self):
        return self.body['meta']['Version']
