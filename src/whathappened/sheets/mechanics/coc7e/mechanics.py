from pathlib import Path
import logging

from whathappened.sheets.mechanics.core import CharacterMechanics
from whathappened.sheets.schema.build import validate

CHARACTER_SCHEMA = Path(__file__).parent / "../../schema/coc7e.json"
assert CHARACTER_SCHEMA.is_file()

logger = logging.getLogger(__name__)


class CoCMechanics(CharacterMechanics):
    def game(self):
        try:
            return (
                self.parent.body["meta"]["GameName"],
                self.parent.body["meta"]["GameType"],
            )
        except Exception as e:
            logger.warning(e)
            return None

    def validate(self, *args, **kwargs):
        return validate(self.parent.body, "coc7e")

    def version(self):
        """Return schema version."""
        return "0.0.5"

    @property
    def name(self):
        return self.parent.body["personalia"]["Name"]

    @property
    def age(self):
        return self.parent.body["personalia"]["Age"]

    @property
    def description(self):
        return self.parent.body["personalia"]["Occupation"]

    @property
    def portrait(self):
        return self.parent.body["personalia"]["Portrait"]

    def skill(self, skill, subskill=None):
        """Return a single skill, or something."""
        skills = self.parent.skills()
        if subskill == "None":
            subskill = None

        for s in skills:
            if s["name"] == skill:
                if subskill is not None and "subskills" not in s:
                    return None
                if subskill is not None:
                    for ss in s["subskills"]:
                        if ss["name"] == subskill:
                            return ss
                    logger.debug("Did not find subskill %s, %s", skill, subskill)
                    return None
                return s

        logger.debug("Did not find %s, %s", skill, subskill)
        return None

    def set_portrait(self, data):
        self.parent.body["personalia"]["Portrait"] = data
        return self.portrait
