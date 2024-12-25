import logging

from whathappened.sheets.mechanics.core import CharacterMechanics

logger = logging.getLogger(__name__)


class CoCMechanics(CharacterMechanics):
    def game(self):
        try:
            return (
                self.parent.body["meta"]["gamename"],
                self.parent.body["meta"]["gametype"],
            )
        except Exception as e:
            logger.warning(e)
            return None

    @property
    def name(self):
        return self.parent.body["character_sheet"]["personalia"]["name"]

    @property
    def age(self):
        return self.parent.body["character_sheet"]["personalia"]["age"]

    @property
    def description(self):
        return self.parent.body["character_sheet"]["personalia"]["occupation"]

    @property
    def portrait(self):
        return self.parent.body["character_sheet"]["personalia"]["portrait"]

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
        self.parent.body["character_sheet"]["personalia"]["Portrait"] = data
        return self.portrait
