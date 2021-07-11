import os
import logging

from ..core import CharacterMechanics
from ..schema import validate

CHARACTER_SCHEMA = os.path.join(
    os.path.dirname(__file__), '../schema/coc7e.yaml')

logger = logging.getLogger(__name__)


class CoCMechanics(CharacterMechanics):
    system = 'coc7e'

    def game(self):
        try:
            return (self.data['meta']['GameName'],
                    self.data['meta']['GameType'])
        except Exception as e:
            logger.warning(e)
            return None

    def validate(self):
        return validate(self.data, CHARACTER_SCHEMA)

    def version(self):
        return '0.0.4'

    @property
    def name(self):
        return self.data['personalia']['Name']

    @property
    def age(self):
        return self.data['personalia']['Age']

    @property
    def description(self):
        return self.data['personalia']['Occupation']

    def portrait(self):
        return self.data['personalia']['Portrait']

    def skill(self, skill, subskill=None):
        """Return a single skill, or something."""
        skills = self.data['skills']
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

    @property
    def skills(self):
        return self.data['skills']

    def add_skill(self, skillname: str, value: int = 1):
        if self.skill(skillname) is not None:
            raise ValueError(f"Skill {skillname} already exists.")

        self.skills.append({"name": skillname,
                            "value": value,
                            "start_value": value})
        if isinstance(self.skills, list):
            self.skills.sort(key=lambda x: x['name'])

    def add_subskill(self, name: str,
                     parent: str,
                     start_value: int = None,
                     value: int = None):
        parent_skill = self.skill(parent)

        if parent_skill is None:
            raise KeyError

        value = value or parent_skill['value']
        start_value = start_value or parent_skill['start_value']
        logger.debug("Try to add subskill")
        logger.debug(f"Name: {name}, parent {parent}, value {value}")
        if self.skill(parent, name) is not None:
            raise ValueError(f"Subskill {name} in {parent} already exists.")

        skill = parent_skill
        if 'subskills' not in skill:
            skill['subskills'] = []
        skill['subskills'].append({
            'name': name,
            'value': value,
            'start_value': start_value
        })

    def set_portrait(self, data):
        self.data['personalia']['Portrait'] = data
        return self.portrait
