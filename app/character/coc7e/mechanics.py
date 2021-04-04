import os
import logging

from ..core import CharacterMechanics
from ..schema import validate

CHARACTER_SCHEMA = os.path.join(os.path.dirname(__file__), '../schema/coc7e.json')

logger = logging.getLogger(__name__)


class CoCMechanics(CharacterMechanics):
    def game(self):
        try:
            return (self.parent.body['meta']['GameName'],
                    self.parent.body['meta']['GameType'])
        except Exception as e:
            logger.warning(e)
            return None

    def validate(self):
        return validate(self.parent.body, CHARACTER_SCHEMA)

    def version(self):
        return '0.0.4'

    @property
    def name(self):
        return self.parent.body['personalia']['Name']

    @property
    def age(self):
        return self.parent.body['personalia']['Age']

    @property
    def description(self):
        return self.parent.body['personalia']['Occupation']

    def portrait(self):
        return self.parent.body['personalia']['Portrait']

    def skill(self, skill, subskill=None):
        """Return a single skill, or something."""
        skills = self.parent.skills()
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

    def set_portrait(self, data):
        self.parent.body['personalia']['Portrait'] = data
        return self.portrait
