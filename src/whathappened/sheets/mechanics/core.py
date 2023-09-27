from functools import reduce
from pathlib import Path
import logging
from typing import Dict, Optional, Type
import base64
import io
from PIL import Image

from whathappened.sheets.schema.build import get_schema, build_from_schema, validate

logger = logging.getLogger(__name__)

CHARACTER_SCHEMA_DIR = Path(__file__).parent.parent / 'schema'

assert CHARACTER_SCHEMA_DIR.is_dir(), CHARACTER_SCHEMA_DIR

GAMES = {}

MECHANICS = {}

GameSystems = []

CHARACTER_SHEET_TEMPLATE = ""


def fix_image(imagedata: str) -> str:
    imagetype, imagedata = imagedata.split(',')
    decoded = base64.b64decode(imagedata)
    buf = io.BytesIO(decoded)
    img = Image.open(buf).convert('RGB')
    img.thumbnail((192, 192))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


class CharacterMechanics():

    def __init__(self, parent):
        self.parent = parent

    def game(self):
        raise NotImplementedError

    def validate(self, *args, **kwargs):
        return validate(self.parent.body, self.parent.system)

    @property
    def name(self):
        logger.error("name: Not implemented")
        return "Unknown property, name"

    @property
    def age(self):
        logger.error("age: Not implemented")
        return "Unknown property, age"

    @property
    def description(self):
        logger.error("description: Not implemented")
        return "Unknown property, description"

    def portrait(self):
        logger.error("portrait: Not implemented")
        return "Unknown property, portrait"

    def store_data(self):
        return

    def skill(self, skill, subskill=None):
        raise NotImplementedError

    def skills(self, *args):
        raise NotImplementedError

    def set_portrait(self, data: str):
        raise NotImplementedError

    def attribute(self, *args):

        path = args[0]

        val = reduce(lambda x, y: x.get(y, None) if x is not None else None, path.split("."), self.parent.body)

        return val

    def set_attribute(self, attribute: Dict):
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
                self.set_portrait(fix_image(data))
        else:
            logger.debug(f"Set '{attribute['field']}' to '{attribute['value']}'")
            s = reduce(lambda x, y: x[y], attribute['field'].split(".")[:-1], self.parent.body)
            s[attribute['field'].split(".")[-1]] = attribute['value']

    def add_skill(self, skillname: str, value: int = 1):
        if self.skill(skillname) is not None:
            raise ValueError(f"Skill {skillname} already exists.")

        self.parent.data['skills'].append({"name": skillname, "value": value, "start_value": value})
        if isinstance(self.parent.data['skills'], list):
            self.parent.data['skills'].sort(key=lambda x: x['name'])

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
        skill['subskills'].append({'name': name, 'value': value, 'start_value': start_value})


def register_game(tag: str, name: str, mechanics: Type[CharacterMechanics] = CharacterMechanics):
    global GameSystems
    GAMES[tag] = name
    MECHANICS[tag] = mechanics

    GameSystems.clear()
    GameSystems += [(k, v) for k, v in GAMES.items()]


def new_character(title: str, system: Optional[str] = None, **kwargs):
    if system is None:
        raise SyntaxError("new_character: System not specified")

    schema_data = get_schema(system)

    nc = build_from_schema(schema_data)
    nc['title'] = title

    return nc


register_game('landf', 'Lasers and feelings')
