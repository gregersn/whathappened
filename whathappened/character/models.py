import logging
from functools import reduce
from typing import Any, Dict, Type, cast
from datetime import datetime
import base64
import io
from PIL import Image

from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import reconstructor, relationship, backref
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Integer, JSON, String

from whathappened.database.base import BaseModel
from whathappened.character.core import CharacterMechanics, MECHANICS
from whathappened.content.mixins import BaseContent

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


class Character(BaseContent, BaseModel):
    __tablename__ = 'charactersheet'
    id = Column(Integer, primary_key=True)
    title = cast(str, Column(String(256)))
    body = cast(Dict[str, Any], Column(JSON))
    timestamp = Column(DateTime,
                       index=True,
                       default=datetime.utcnow,
                       onupdate=datetime.utcnow)
    user_id = cast(int, Column(Integer, ForeignKey('user_profile.id')))
    player = relationship('UserProfile',
                          backref=backref('characters', lazy='dynamic'))

    folder = relationship('Folder', backref='characters')

    _default_fields = ['id', 'title', 'body', 'timestamp', 'user_id']

    def __repr__(self):
        return '<Character {}>'.format(self.title)

    def __init__(self,
                 mechanics: Type[CharacterMechanics] = CharacterMechanics,
                 *args,
                 **kwargs):
        super(Character, self).__init__(*args, **kwargs)
        self._data = None
        # Add a subclass or something that
        # has the mechanics of the character.
        self.mechanics = mechanics(self)

    @reconstructor
    def init_on_load(self):
        system = self.data.get('system', '')
        logger.debug(f"Loading character of type {system}")
        system = self.system
        self.mechanics = MECHANICS.get(system, CharacterMechanics)(self)

    @property
    def data(self) -> Dict[str, Any]:
        if isinstance(self.body, dict):
            return self.body
        raise TypeError("Body is not a dictionary")

    @property
    def system(self) -> str:
        s = self.data.get('system', None)
        if s is not None:
            return s

        logger.warning("Deprecation: Outdated character data")
        default = "Call of Cthulhu TM"
        if self.data.get('meta', {}).get('GameName') == default:
            logger.warning("Trying old CoC stuff.")
            return "coc7e"

        return "Unknown"

    @property
    def version(self):
        v = self.data.get('version', None)
        return v

    @property
    def game(self):
        return self.mechanics.game()

    def validate(self):
        return self.mechanics.validate()

    def get_sheet(self):
        return self.data

    @property
    def name(self):
        return self.mechanics.name

    @property
    def age(self):
        return self.mechanics.age

    @property
    def portrait(self):
        return self.mechanics.portrait()

    @property
    def description(self):
        return self.mechanics.description

    def attribute(self, *args):

        path = args[0]

        val = reduce(lambda x, y: x.get(y, None) if x is not None else None,
                     path.split("."), self.data)

        return val

    def set_attribute(self, attribute: Dict):
        """Set a specific attribute."""

        if attribute.get('category', None) == 'skill':
            logger.debug("Set a skill")
            datatype = attribute.get('type', 'string')
            skill = attribute['field']
            subfield = attribute.get('subfield', None)
            value = attribute.get('value')

            if datatype == 'number' and not isinstance(value, int):
                value = None

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
            if data is not None:
                self.mechanics.set_portrait(fix_image(data))
        else:
            logger.debug(
                f"Set '{attribute['field']}' to '{attribute['value']}'")
            s = reduce(lambda x, y: x[y], attribute['field'].split(".")[:-1],
                       self.data)
            s[attribute['field'].split(".")[-1]] = attribute['value']

    def store_data(self):
        """Mark data as modified."""
        flag_modified(self, "body")

    def skill(self, *args, **kwargs):
        return self.mechanics.skill(*args, **kwargs)

    def skills(self, *args):
        """Return a list of skills."""
        return self.data['skills']

    def add_skill(self, skillname: str, value: int = 1):
        if self.skill(skillname) is not None:
            raise ValueError(f"Skill {skillname} already exists.")

        self.data['skills'].append({
            "name": skillname,
            "value": value,
            "start_value": value
        })
        if isinstance(self.data['skills'], list):
            self.data['skills'].sort(key=lambda x: x['name'])

    def add_subskill(self, name: str, parent: str):
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

    @property
    def schema_version(self):
        return self.data['meta']['Version']
